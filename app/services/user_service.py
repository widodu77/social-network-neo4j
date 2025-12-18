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
        """
        Initialize user service.

        Args:
            driver: Neo4j driver instance (optional, will create if not provided)
        """
        self._driver = driver or get_neo4j_driver()

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

        with self._driver.session() as session:
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

            # Add skills and company if provided
            self._add_user_relationships(user_id, user_data.skills, user_data.company)

            return self._record_to_user(record)

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

        with self._driver.session() as session:
            result = session.run(query, user_id=user_id)
            record = result.single()

            if not record:
                return None

            return self._record_to_user_response(record)

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

        with self._driver.session() as session:
            result = session.run(query, limit=limit, offset=offset)
            return [self._record_to_user(record) for record in result]

    def _add_user_relationships(self, user_id: str, skills: Optional[List[str]], company: Optional[str]) -> None:
        """
        Add skills and company relationships to a user.

        Args:
            user_id: User ID
            skills: List of skill names
            company: Company name
        """
        if skills:
            for skill_name in skills:
                self._add_skill_to_user(user_id, skill_name)

        if company:
            self._add_company_to_user(user_id, company)

    def _add_skill_to_user(self, user_id: str, skill_name: str) -> None:
        """
        Add a skill to a user.

        Args:
            user_id: User ID
            skill_name: Skill name
        """
        query = """
        MATCH (u:User {user_id: $user_id})
        MERGE (s:Skill {name: $skill_name})
        MERGE (u)-[:HAS_SKILL]->(s)
        """
        with self._driver.session() as session:
            session.run(query, user_id=user_id, skill_name=skill_name)

    def _add_company_to_user(self, user_id: str, company_name: str) -> None:
        """
        Add a company relationship to a user.

        Args:
            user_id: User ID
            company_name: Company name
        """
        query = """
        MATCH (u:User {user_id: $user_id})
        MERGE (c:Company {name: $company_name})
        MERGE (u)-[:WORKS_AT]->(c)
        """
        with self._driver.session() as session:
            session.run(query, user_id=user_id, company_name=company_name)

    @staticmethod
    def _record_to_user(record) -> User:
        """
        Convert a Neo4j record to a User model.

        Args:
            record: Neo4j record

        Returns:
            User instance
        """
        return User(
            user_id=record["user_id"],
            name=record["name"],
            email=record["email"],
            title=record["title"],
            location=record["location"],
            bio=record["bio"],
            connection_count=record.get("connection_count", 0),
            skill_count=record.get("skill_count", 0),
        )

    @staticmethod
    def _record_to_user_response(record) -> UserResponse:
        """
        Convert a Neo4j record to a UserResponse model.

        Args:
            record: Neo4j record

        Returns:
            UserResponse instance
        """
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
