"""
LLM-powered knowledge graph query models.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class LLMQueryRequest(BaseModel):
    """LLM-powered natural language query request."""

    query: str = Field(
        ..., description="Natural language query about the graph", example="Who are the most connected users?"
    )
    user_id: Optional[str] = Field(None, description="Optional user context for personalized queries")


class LLMQueryResponse(BaseModel):
    """LLM-powered query response."""

    natural_query: str
    cypher_query: str
    results: List[dict]
    explanation: str
    query_type: str
