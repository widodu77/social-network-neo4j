"""
User service for business logic related to users.
"""

from typing import List, Optional
from neo4j import Driver
from app.models.user import UserCreate, User, UserResponse
from app.database import get_neo4j_driver


class UserService:
    """Service class for user-related operations."""

    def __init__(self, driver: Optional[Driver] = None):
        """Initialize user service."""
        self.driver = driver or get_neo4j_driver()

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user in the database.

        Args:
            user_data: User creation data

        Returns:
            Created user
        """
        query = """
        CREATE (u:User {
            user_id: randomUUID(),
            name: $name,
            email: $email,
            title: $title,
            location: $location,
            bio: $bio,
            created_at: datetime()
        })
        RETURN u.user_id AS user_id, u.name AS name, u.email AS email,
               u.title AS title, u.location AS location, u.bio AS bio
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                name=user_data.name,
                email=user_data.email,
                title=user_data.title,
                location=user_data.location,
                bio=user_data.bio,
            )
            record = result.single()

            user_id = record["user_id"]

            # Add skills if provided
            if user_data.skills:
                for skill_name in user_data.skills:
                    self._add_skill_to_user(user_id, skill_name)

            # Add company if provided
            if user_data.company:
                self._add_company_to_user(user_id, user_data.company)

            return User(
                user_id=user_id,
                name=record["name"],
                email=record["email"],
                title=record["title"],
                location=record["location"],
                bio=record["bio"],
            )

    def get_user(self, user_id: str) -> Optional[UserResponse]:
        """
        Get user by ID with full details.

        Args:
            user_id: User ID

        Returns:
            User details or None
        """
        query = """
        MATCH (u:User {user_id: $user_id})
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(s:Skill)
        OPTIONAL MATCH (u)-[:WORKS_AT]->(c:Company)
        OPTIONAL MATCH (u)-[:KNOWS]-(conn:User)
        RETURN u.user_id AS user_id, u.name AS name, u.email AS email,
               u.title AS title, u.location AS location, u.bio AS bio,
               COLLECT(DISTINCT s.name) AS skills,
               c.name AS company,
               COLLECT(DISTINCT conn.user_id) AS connections
        """

        with self.driver.session() as session:
            result = session.run(query, user_id=user_id)
            record = result.single()

            if not record:
                return None

            return UserResponse(
                user_id=record["user_id"],
                name=record["name"],
                email=record["email"],
                title=record["title"],
                location=record["location"],
                bio=record["bio"],
                skills=[s for s in record["skills"] if s],
                company=record["company"],
                connections=[c for c in record["connections"] if c],
            )

    def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """
        List all users with pagination.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of users
        """
        query = """
        MATCH (u:User)
        OPTIONAL MATCH (u)-[:KNOWS]-(conn:User)
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(s:Skill)
        WITH u, COUNT(DISTINCT conn) AS connection_count, COUNT(DISTINCT s) AS skill_count
        RETURN u.user_id AS user_id, u.name AS name, u.email AS email,
               u.title AS title, u.location AS location, u.bio AS bio,
               connection_count, skill_count
        ORDER BY u.name
        SKIP $offset
        LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(query, limit=limit, offset=offset)
            return [
                User(
                    user_id=record["user_id"],
                    name=record["name"],
                    email=record["email"],
                    title=record["title"],
                    location=record["location"],
                    bio=record["bio"],
                    connection_count=record["connection_count"],
                    skill_count=record["skill_count"],
                )
                for record in result
            ]

    def _add_skill_to_user(self, user_id: str, skill_name: str):
        """Add a skill to a user."""
        query = """
        MATCH (u:User {user_id: $user_id})
        MERGE (s:Skill {name: $skill_name})
        MERGE (u)-[:HAS_SKILL]->(s)
        """
        with self.driver.session() as session:
            session.run(query, user_id=user_id, skill_name=skill_name)

    def _add_company_to_user(self, user_id: str, company_name: str):
        """Add a company relationship to a user."""
        query = """
        MATCH (u:User {user_id: $user_id})
        MERGE (c:Company {name: $company_name})
        MERGE (u)-[:WORKS_AT]->(c)
        """
        with self.driver.session() as session:
            session.run(query, user_id=user_id, company_name=company_name)
