"""
Neo4j database connection management.
"""
import os
from typing import Optional
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv

load_dotenv()


class Neo4jConnection:
    """
    Neo4j database connection manager with context manager support.
    """

    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j connection.

        Args:
            uri: Neo4j connection URI
            user: Database username
            password: Database password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self._driver: Optional[Driver] = None

    def connect(self) -> Driver:
        """
        Establish connection to Neo4j database.

        Returns:
            Neo4j driver instance
        """
        if self._driver is None:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self._driver

    def close(self):
        """Close the database connection."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def verify_connectivity(self) -> bool:
        """
        Verify database connectivity.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            driver = self.connect()
            driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            return False

    def execute_query(self, query: str, parameters: dict = None):
        """
        Execute a Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Query results
        """
        driver = self.connect()
        with driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write(self, query: str, parameters: dict = None):
        """
        Execute a write transaction.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Query results
        """
        driver = self.connect()
        with driver.session() as session:
            result = session.execute_write(lambda tx: tx.run(query, parameters or {}))
            return result

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global driver instance
_driver: Optional[Driver] = None


def get_neo4j_driver() -> Driver:
    """
    Get or create Neo4j driver instance (singleton pattern).

    Returns:
        Neo4j driver instance
    """
    global _driver
    if _driver is None:
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password123")
        _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver


def close_neo4j_driver():
    """Close the global Neo4j driver instance."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
