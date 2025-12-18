"""
Recommendation service for friend and job recommendations.
"""

from typing import List, Optional
from neo4j import Driver
from app.models.recommendation import FriendRecommendation, JobRecommendation, PersonSuggestion
from app.database import get_neo4j_driver


class RecommendationService:
    """Service class for recommendation operations."""

    def __init__(self, driver: Optional[Driver] = None):
        """Initialize recommendation service."""
        self.driver = driver or get_neo4j_driver()

    def get_friend_recommendations(self, user_id: str, limit: int = 10) -> List[FriendRecommendation]:
        """
        Get friend recommendations based on mutual connections.

        Args:
            user_id: User ID
            limit: Maximum number of recommendations

        Returns:
            List of friend recommendations
        """
        query = """
        MATCH (u:User {user_id: $user_id})-[:KNOWS]-(friend)-[:KNOWS]-(recommendation:User)
        WHERE u <> recommendation
        AND NOT (u)-[:KNOWS]-(recommendation)

        WITH recommendation, COUNT(DISTINCT friend) AS mutual_count

        OPTIONAL MATCH (u:User {user_id: $user_id})-[:HAS_SKILL]->(s:Skill)<-[:HAS_SKILL]-(recommendation)

        WITH recommendation, mutual_count, COLLECT(DISTINCT s.name) AS common_skills

        WITH recommendation, mutual_count, common_skills,
             (mutual_count * 0.6 + SIZE(common_skills) * 0.4) / 10.0 AS score

        RETURN recommendation.user_id AS user_id,
               recommendation.name AS name,
               recommendation.title AS title,
               mutual_count AS mutual_connections,
               common_skills,
               CASE
                   WHEN score > 1.0 THEN 1.0
                   ELSE score
               END AS score,
               CASE
                   WHEN mutual_count > 5 THEN 'Many mutual connections'
                   WHEN SIZE(common_skills) > 3 THEN 'Similar skills'
                   ELSE 'Mutual connections'
               END AS reason
        ORDER BY score DESC, mutual_count DESC
        LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, user_id=user_id, limit=limit)
            return [
                FriendRecommendation(
                    user_id=record["user_id"],
                    name=record["name"],
                    title=record["title"],
                    mutual_connections=record["mutual_connections"],
                    common_skills=record["common_skills"],
                    score=record["score"],
                    reason=record["reason"],
                )
                for record in result
            ]

    def get_job_recommendations(self, user_id: str, limit: int = 10) -> List[JobRecommendation]:
        """
        Get job recommendations based on user skills.

        Note: This is a placeholder. In a real system, you'd have Job nodes.
        For now, we'll recommend companies where users with similar skills work.

        Args:
            user_id: User ID
            limit: Maximum number of recommendations

        Returns:
            List of job recommendations
        """
        query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_SKILL]->(skill:Skill)
        WITH u, COLLECT(skill.name) AS user_skills

        MATCH (other:User)-[:HAS_SKILL]->(s:Skill)
        WHERE other <> u AND s.name IN user_skills

        MATCH (other)-[:WORKS_AT]->(c:Company)
        WHERE NOT (u)-[:WORKS_AT]->(c)

        WITH c, user_skills, COLLECT(DISTINCT s.name) AS company_skills

        WITH c, user_skills, company_skills,
             SIZE([skill IN company_skills WHERE skill IN user_skills]) AS matching_count,
             SIZE(company_skills) AS total_skills

        WITH c, user_skills, company_skills,
             matching_count,
             CASE
                 WHEN total_skills > 0 THEN toFloat(matching_count) / total_skills
                 ELSE 0.0
             END AS match_rate

        WHERE match_rate > 0.3

        RETURN 'job_' + c.name AS job_id,
               'Position at ' + c.name AS title,
               c.name AS company,
               c.location AS location,
               company_skills AS required_skills,
               [skill IN company_skills WHERE skill IN user_skills] AS matching_skills,
               match_rate AS skill_match_rate,
               match_rate AS score
        ORDER BY score DESC
        LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, user_id=user_id, limit=limit)
            return [
                JobRecommendation(
                    job_id=record["job_id"],
                    title=record["title"],
                    company=record["company"],
                    location=record["location"],
                    required_skills=record["required_skills"],
                    matching_skills=record["matching_skills"],
                    skill_match_rate=record["skill_match_rate"],
                    score=record["score"],
                )
                for record in result
            ]

    def get_people_suggestions(self, user_id: str, limit: int = 10) -> List[PersonSuggestion]:
        """
        Get "people you may know" suggestions.
        Combines multiple signals: mutual connections, common skills, same company.

        Args:
            user_id: User ID
            limit: Maximum number of suggestions

        Returns:
            List of person suggestions
        """
        query = """
        MATCH (u:User {user_id: $user_id})
        OPTIONAL MATCH (u)-[:KNOWS]-(friend)
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(skill)
        OPTIONAL MATCH (u)-[:WORKS_AT]->(company)

        WITH u,
             COLLECT(DISTINCT friend) AS friends,
             COLLECT(DISTINCT skill) AS user_skills,
             company

        MATCH (suggestion:User)
        WHERE suggestion <> u
        AND NOT suggestion IN friends
        AND NOT (u)-[:KNOWS]-(suggestion)

        OPTIONAL MATCH (suggestion)-[:KNOWS]-(mutual)
        WHERE mutual IN friends

        OPTIONAL MATCH (suggestion)-[:HAS_SKILL]->(common_skill)
        WHERE common_skill IN user_skills

        OPTIONAL MATCH (suggestion)-[:WORKS_AT]->(suggestion_company)

        WITH u, suggestion,
             COUNT(DISTINCT mutual) AS mutual_count,
             COUNT(DISTINCT common_skill) AS common_skill_count,
             suggestion_company,
             company,
             suggestion.name AS name,
             suggestion.title AS title

        WHERE mutual_count > 0 OR common_skill_count > 0 OR (company IS NOT NULL AND suggestion_company = company)

        WITH suggestion, name, title, suggestion_company.name AS company_name,
             mutual_count, common_skill_count,
             CASE WHEN company IS NOT NULL AND suggestion_company = company THEN true ELSE false END AS same_company

        WITH suggestion, name, title, company_name, mutual_count, common_skill_count, same_company,
             (mutual_count * 0.5 + common_skill_count * 0.3 + CASE WHEN same_company THEN 2 ELSE 0 END) / 10.0 AS score

        OPTIONAL MATCH path = shortestPath((u:User {user_id: $user_id})-[:KNOWS*]-(suggestion))

        RETURN suggestion.user_id AS user_id,
               name,
               title,
               company_name,
               mutual_count AS mutual_connections,
               common_skill_count AS common_skills,
               same_company,
               CASE
                   WHEN path IS NOT NULL THEN LENGTH(path)
                   ELSE NULL
               END AS connection_path_length,
               CASE
                   WHEN score > 1.0 THEN 1.0
                   ELSE score
               END AS score
        ORDER BY score DESC, mutual_count DESC
        LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, user_id=user_id, limit=limit)
            return [
                PersonSuggestion(
                    user_id=record["user_id"],
                    name=record["name"],
                    title=record["title"],
                    company=record["company_name"],
                    mutual_connections=record["mutual_connections"],
                    common_skills=record["common_skills"],
                    same_company=record["same_company"],
                    connection_path_length=record["connection_path_length"],
                    score=record["score"],
                )
                for record in result
            ]
