"""
Path service for shortest path queries.
"""
from typing import Optional
from neo4j import Driver
from app.models.path import ShortestPath, PathNode
from app.database import get_neo4j_driver


class PathService:
    """Service class for path-related operations."""

    def __init__(self, driver: Optional[Driver] = None):
        """Initialize path service."""
        self.driver = driver or get_neo4j_driver()

    def find_shortest_path(self, from_user_id: str, to_user_id: str) -> ShortestPath:
        """
        Find the shortest path between two users in the network.

        Args:
            from_user_id: Starting user ID
            to_user_id: Target user ID

        Returns:
            Shortest path information
        """
        query = """
        MATCH (from:User {user_id: $from_user_id})
        MATCH (to:User {user_id: $to_user_id})

        OPTIONAL MATCH path = shortestPath((from)-[:KNOWS*]-(to))

        WITH from, to, path,
             CASE WHEN path IS NOT NULL THEN LENGTH(path) ELSE -1 END AS path_length,
             CASE WHEN path IS NOT NULL THEN nodes(path) ELSE [] END AS path_nodes

        UNWIND CASE WHEN SIZE(path_nodes) > 0 THEN path_nodes ELSE [null] END AS node

        OPTIONAL MATCH (node)-[:WORKS_AT]->(company:Company)

        WITH from, to, path_length, path_nodes,
             COLLECT({
                 user_id: node.user_id,
                 name: node.name,
                 title: node.title,
                 company: company.name
             }) AS node_details

        RETURN path_length,
               CASE
                   WHEN path_length >= 0 THEN node_details
                   ELSE []
               END AS nodes,
               path_length >= 0 AS exists
        """

        with self.driver.session() as session:
            result = session.run(
                query, from_user_id=from_user_id, to_user_id=to_user_id
            )
            record = result.single()

            if not record:
                return ShortestPath(
                    from_user_id=from_user_id,
                    to_user_id=to_user_id,
                    path_length=0,
                    nodes=[],
                    exists=False,
                )

            nodes = []
            if record["exists"] and record["nodes"]:
                nodes = [
                    PathNode(
                        user_id=node["user_id"],
                        name=node["name"],
                        title=node["title"],
                        company=node["company"],
                    )
                    for node in record["nodes"]
                    if node["user_id"] is not None
                ]

            return ShortestPath(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                path_length=max(0, record["path_length"]),
                nodes=nodes,
                exists=record["exists"],
            )
