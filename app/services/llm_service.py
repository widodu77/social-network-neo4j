"""
LLM-powered knowledge graph query service.
This uses a simple template-based approach for demonstration.
In production, you would integrate with OpenAI/Anthropic APIs.
"""
from typing import Dict, Optional
from neo4j import Driver
from app.models.llm import LLMQueryResponse
from app.database import get_neo4j_driver


class LLMQueryService:
    """Service for LLM-powered natural language graph queries."""

    def __init__(self, driver: Optional[Driver] = None):
        """Initialize LLM query service."""
        self.driver = driver or get_neo4j_driver()

        # Template mappings for common queries
        self.query_templates = {
            "most connected": {
                "cypher": """
                    MATCH (u:User)-[r:KNOWS]-()
                    WITH u, COUNT(r) AS connections
                    RETURN u.user_id AS user_id, u.name AS name,
                           u.title AS title, connections
                    ORDER BY connections DESC
                    LIMIT 10
                """,
                "explanation": "Finding users with the most connections in the network"
            },
            "popular skills": {
                "cypher": """
                    MATCH (u:User)-[:HAS_SKILL]->(s:Skill)
                    WITH s, COUNT(u) AS user_count
                    RETURN s.name AS skill, s.category AS category, user_count
                    ORDER BY user_count DESC
                    LIMIT 10
                """,
                "explanation": "Finding the most popular skills among users"
            },
            "top companies": {
                "cypher": """
                    MATCH (u:User)-[:WORKS_AT]->(c:Company)
                    WITH c, COUNT(u) AS employee_count
                    RETURN c.name AS company, c.industry AS industry, employee_count
                    ORDER BY employee_count DESC
                    LIMIT 10
                """,
                "explanation": "Finding companies with the most employees in the network"
            },
            "ml developers": {
                "cypher": """
                    MATCH (u:User)
                    WHERE u.title CONTAINS 'Data' OR u.title CONTAINS 'ML'
                    OPTIONAL MATCH (u)-[:KNOWS]-(friend)
                    WITH u, COUNT(friend) AS connections
                    RETURN u.user_id AS user_id, u.name AS name,
                           u.title AS title, connections
                    ORDER BY connections DESC
                    LIMIT 10
                """,
                "explanation": "Finding ML/Data Science developers and their network size"
            },
            "web developers": {
                "cypher": """
                    MATCH (u:User)
                    WHERE u.title CONTAINS 'Web'
                    OPTIONAL MATCH (u)-[:KNOWS]-(friend)
                    WITH u, COUNT(friend) AS connections
                    RETURN u.user_id AS user_id, u.name AS name,
                           u.title AS title, connections
                    ORDER BY connections DESC
                    LIMIT 10
                """,
                "explanation": "Finding Web developers and their network size"
            },
            "skill distribution": {
                "cypher": """
                    MATCH (s:Skill)<-[:HAS_SKILL]-(u:User)
                    WITH s.category AS category, COUNT(DISTINCT s) AS skill_count,
                         COUNT(u) AS user_count
                    RETURN category, skill_count, user_count
                    ORDER BY user_count DESC
                """,
                "explanation": "Analyzing skill distribution across categories"
            },
            "network statistics": {
                "cypher": """
                    MATCH (u:User)
                    WITH COUNT(u) AS total_users
                    MATCH (s:Skill)
                    WITH total_users, COUNT(s) AS total_skills
                    MATCH (c:Company)
                    WITH total_users, total_skills, COUNT(c) AS total_companies
                    MATCH ()-[r:KNOWS]-()
                    WITH total_users, total_skills, total_companies, COUNT(DISTINCT r) AS total_connections
                    RETURN total_users, total_skills, total_companies, total_connections
                """,
                "explanation": "Getting overall network statistics"
            }
        }

    def process_natural_language_query(self, query: str, user_id: Optional[str] = None) -> LLMQueryResponse:
        """
        Process a natural language query and convert it to Cypher.

        This is a simplified implementation using template matching.
        In production, you would use LLM APIs (OpenAI, Anthropic) to generate Cypher.

        Args:
            query: Natural language query
            user_id: Optional user context

        Returns:
            Query results with explanation
        """
        query_lower = query.lower()

        # Find matching template
        matched_template = None
        matched_key = None

        for key, template in self.query_templates.items():
            if key in query_lower:
                matched_template = template
                matched_key = key
                break

        # Default fallback query
        if not matched_template:
            matched_template = {
                "cypher": """
                    MATCH (u:User)
                    RETURN u.user_id AS user_id, u.name AS name, u.title AS title
                    LIMIT 10
                """,
                "explanation": "Showing sample users (query not recognized, showing default results)"
            }
            matched_key = "default"

        # Execute the Cypher query
        with self.driver.session() as session:
            result = session.run(matched_template["cypher"])
            results = [dict(record) for record in result]

        return LLMQueryResponse(
            natural_query=query,
            cypher_query=matched_template["cypher"].strip(),
            results=results,
            explanation=matched_template["explanation"],
            query_type=matched_key
        )

    def get_user_insights(self, user_id: str) -> Dict:
        """
        Get AI-powered insights about a specific user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with user insights
        """
        query = """
        MATCH (u:User {user_id: $userId})
        OPTIONAL MATCH (u)-[:KNOWS]-(friend)
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(skill)
        OPTIONAL MATCH (u)-[:WORKS_AT]->(company)

        WITH u, company,
             COUNT(DISTINCT friend) AS connection_count,
             COLLECT(DISTINCT skill.name) AS skills

        // Calculate network strength
        OPTIONAL MATCH (u)-[:KNOWS]-(f1)-[:KNOWS]-(f2)
        WHERE (u)-[:KNOWS]-(f2) AND f1 <> f2
        WITH u, company, connection_count, skills,
             COUNT(DISTINCT [f1, f2]) AS triangles

        RETURN u.user_id AS user_id,
               u.name AS name,
               u.title AS title,
               company.name AS company,
               connection_count,
               skills,
               triangles,
               CASE
                   WHEN connection_count > 20 THEN 'Highly Connected'
                   WHEN connection_count > 10 THEN 'Well Connected'
                   WHEN connection_count > 5 THEN 'Moderately Connected'
                   ELSE 'Limited Connections'
               END AS network_status,
               CASE
                   WHEN triangles > 10 THEN 'Strong network clustering'
                   WHEN triangles > 5 THEN 'Moderate clustering'
                   ELSE 'Low clustering'
               END AS clustering_insight
        """

        with self.driver.session() as session:
            result = session.run(query, userId=user_id)
            record = result.single()

            if not record:
                return {"error": "User not found"}

            return dict(record)
