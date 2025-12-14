"""
Path model definitions for shortest path queries.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class PathNode(BaseModel):
    """Node in a path."""

    user_id: str = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    title: Optional[str] = Field(None, description="Job title")
    company: Optional[str] = Field(None, description="Company name")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ShortestPath(BaseModel):
    """Shortest path between two users."""

    from_user_id: str = Field(..., description="Starting user ID")
    to_user_id: str = Field(..., description="Target user ID")
    path_length: int = Field(..., ge=0, description="Number of hops in the path")
    nodes: List[PathNode] = Field(..., description="Ordered list of nodes in the path")
    exists: bool = Field(..., description="Whether a path exists")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
