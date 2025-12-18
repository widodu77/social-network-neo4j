"""
LLM-powered knowledge graph query service using OpenAI.
Converts natural language queries into Neo4j Cypher queries.
"""

import os
from typing import Dict, Optional, Tuple
from openai import OpenAI
from neo4j import Driver
from app.models.llm import LLMQueryResponse
from app.database import get_neo4j_driver


class LLMQueryService:
    """Service for LLM-powered natural language graph queries."""

    # Schema description for the LLM (class-level constant)
    SCHEMA_CONTEXT = """
        Neo4j Graph Schema:

        Nodes:
        - User (properties: user_id, name, email, title, location, bio)
        - Skill (properties: name, category)
        - Company (properties: name, industry, size, location)

        Relationships:
        - (User)-[:KNOWS]->(User) - friendship/connection
        - (User)-[:HAS_SKILL]->(Skill) - user's skills
        - (User)-[:WORKS_AT]->(Company) - employment

        Constraints:
        - User.user_id is UNIQUE
        - User.email is UNIQUE
        - Skill.name is UNIQUE
        - Company.name is UNIQUE

        Common Query Patterns:
        - Find connected users: MATCH (u:User)-[:KNOWS]-(friend)
        - Find users with skills: MATCH (u:User)-[:HAS_SKILL]->(s:Skill)
        - Count connections: MATCH (u)-[:KNOWS]-() WITH u, COUNT(*) AS connections
        - Find colleagues: MATCH (u1:User)-[:WORKS_AT]->(c)<-[:WORKS_AT]-(u2:User)
        """

    def __init__(self, driver: Optional[Driver] = None, client: Optional[OpenAI] = None):
        """
        Initialize LLM query service.

        Args:
            driver: Neo4j driver instance (optional, will create if not provided)
            client: OpenAI client instance (optional, will create if not provided)
        """
        self._driver = driver or get_neo4j_driver()
        self._client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def process_natural_language_query(self, query: str, user_id: Optional[str] = None) -> LLMQueryResponse:
        """
        Process a natural language query and convert it to Cypher using OpenAI.

        Args:
            query: Natural language query
            user_id: Optional user context

        Returns:
            Query results with explanation
        """
        try:
            # Generate Cypher query using OpenAI
            cypher_query, explanation, query_type = self._generate_cypher_with_llm(query, user_id)

            # Execute the Cypher query
            with self._driver.session() as session:
                result = session.run(cypher_query)
                results = [dict(record) for record in result]

            return LLMQueryResponse(
                natural_query=query,
                cypher_query=cypher_query,
                results=results,
                explanation=explanation,
                query_type=query_type,
            )

        except Exception as e:
            # Fallback to simple query on error
            return self._fallback_query(query, str(e))

    def _generate_cypher_with_llm(self, query: str, user_id: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Use OpenAI to generate a Cypher query from natural language.

        Args:
            query: Natural language query
            user_id: Optional user context

        Returns:
            Tuple of (cypher_query, explanation, query_type)
        """
        user_context = f"\nContext: Query is for user_id '{user_id}'" if user_id else ""

        prompt = f"""You are a Neo4j Cypher query expert. Given a natural language query, generate a valid Cypher query.

{self.SCHEMA_CONTEXT}
{user_context}

User Query: {query}

Generate a Cypher query that answers this question. Return your response in this EXACT format:

CYPHER:
[Your Cypher query here]

EXPLANATION:
[Brief explanation of what the query does]

TYPE:
[One-word category: connections/skills/companies/statistics/general]

Important:
- Return valid Cypher syntax only
- Use LIMIT 10 by default unless user specifies otherwise
- Use parameterized queries when possible
- Order results meaningfully (DESC for counts, alphabetically for names)
- Handle cases where data might not exist (use OPTIONAL MATCH when appropriate)
"""

        response = self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Neo4j Cypher query generator."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,  # Low temperature for consistent, accurate queries
            max_tokens=500,
        )

        # Parse the response
        content = response.choices[0].message.content
        cypher_query, explanation, query_type = self._parse_llm_response(content)

        return cypher_query, explanation, query_type

    def _parse_llm_response(self, content: str) -> Tuple[str, str, str]:
        """
        Parse the LLM response to extract Cypher query, explanation, and type.

        Args:
            content: Raw LLM response

        Returns:
            Tuple of (cypher_query, explanation, query_type)
        """
        cypher_query = ""
        explanation = ""
        query_type = "general"

        try:
            # Split by sections
            parts = content.split("CYPHER:")
            if len(parts) > 1:
                cypher_part = parts[1].split("EXPLANATION:")[0].strip()
                cypher_query = cypher_part.strip()

            parts = content.split("EXPLANATION:")
            if len(parts) > 1:
                explanation_part = parts[1].split("TYPE:")[0].strip()
                explanation = explanation_part.strip()

            parts = content.split("TYPE:")
            if len(parts) > 1:
                query_type = parts[1].strip().lower()

        except Exception:
            # If parsing fails, try to extract just the Cypher query
            lines = content.split("\n")
            cypher_lines = []
            in_cypher = False

            for line in lines:
                if "MATCH" in line.upper() or "RETURN" in line.upper() or "WITH" in line.upper():
                    in_cypher = True
                if in_cypher:
                    if "EXPLANATION" in line or "TYPE" in line:
                        break
                    cypher_lines.append(line)

            cypher_query = "\n".join(cypher_lines).strip()
            explanation = "Query generated from natural language"

        # Clean up Cypher query (remove markdown code blocks if present)
        cypher_query = cypher_query.replace("```cypher", "").replace("```", "").strip()

        return cypher_query, explanation, query_type

    def _fallback_query(self, query: str, error: str) -> LLMQueryResponse:
        """
        Fallback query when LLM generation fails.

        Args:
            query: Original natural language query
            error: Error message

        Returns:
            LLMQueryResponse with default results
        """
        fallback_cypher = """
            MATCH (u:User)
            RETURN u.user_id AS user_id, u.name AS name, u.title AS title
            LIMIT 10
        """

        try:
            with self._driver.session() as session:
                result = session.run(fallback_cypher)
                results = [dict(record) for record in result]
        except Exception:
            results = []

        return LLMQueryResponse(
            natural_query=query,
            cypher_query=fallback_cypher.strip(),
            results=results,
            explanation=f"Query generation failed: {error}. Showing sample users.",
            query_type="fallback",
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

        with self._driver.session() as session:
            result = session.run(query, userId=user_id)
            record = result.single()

            if not record:
                return {"error": "User not found"}

            return dict(record)
