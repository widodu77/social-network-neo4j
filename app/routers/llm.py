"""
LLM-powered knowledge graph query endpoints.
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from app.models.llm import LLMQueryRequest, LLMQueryResponse
from app.services.llm_service import LLMQueryService

router = APIRouter()


def get_llm_service() -> LLMQueryService:
    """
    Dependency to get LLM service instance.
    Only initializes if OPENAI_API_KEY is set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="LLM service unavailable: OPENAI_API_KEY not configured")
    return LLMQueryService()


@router.post("/query", response_model=LLMQueryResponse)
async def query_with_natural_language(
    request: LLMQueryRequest, llm_service: LLMQueryService = Depends(get_llm_service)
):
    """
    Query the knowledge graph using natural language (LLM-powered).

    This endpoint translates natural language queries into Cypher and executes them.
    It demonstrates AI-powered knowledge graph interaction.

    **Example queries:**
    - "Who are the most connected users?"
    - "What are the popular skills?"
    - "Show me ML developers"
    - "Show me web developers"
    - "What are the network statistics?"
    - "Show me top companies"
    - "What is the skill distribution?"

    **How it works:**
    1. **Prompt Processing**: Natural language query is analyzed
    2. **Cypher Generation**: Query is converted to Cypher (template-based for demo)
    3. **Execution**: Cypher is executed against Neo4j
    4. **Response**: Results are returned with explanation

    **Note:** This is a template-based implementation for demonstration.
    In production, integrate with OpenAI/Anthropic APIs for dynamic query generation.
    """
    try:
        return llm_service.process_natural_language_query(query=request.query, user_id=request.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/users/{user_id}/insights")
async def get_user_network_insights(user_id: str, llm_service: LLMQueryService = Depends(get_llm_service)):
    """
    Get AI-powered insights about a specific user's network.

    This uses graph algorithms and pattern analysis to provide insights like:
    - Network strength and size
    - Clustering coefficient
    - Connection patterns
    - Network positioning

    **Example response:**
    ```json
    {
        "user_id": "user-1",
        "name": "John Doe",
        "connection_count": 15,
        "network_status": "Well Connected",
        "clustering_insight": "Moderate clustering",
        "triangles": 8
    }
    ```
    """
    try:
        insights = llm_service.get_user_insights(user_id=user_id)
        if "error" in insights:
            raise HTTPException(status_code=404, detail=insights["error"])
        return insights
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/examples")
async def get_example_queries():
    """
    Get a list of example natural language queries you can try.

    This helps users understand what kinds of questions they can ask.
    """
    return {
        "examples": [
            {
                "query": "Who are the most connected users?",
                "description": "Find users with the most connections in the network",
            },
            {"query": "What are the popular skills?", "description": "Discover the most in-demand skills"},
            {"query": "Show me ML developers", "description": "Find machine learning and data science professionals"},
            {"query": "Show me web developers", "description": "Find web development professionals"},
            {
                "query": "What are the network statistics?",
                "description": "Get overall statistics about the social network",
            },
            {"query": "Show me top companies", "description": "Find companies with the most employees in the network"},
            {
                "query": "What is the skill distribution?",
                "description": "Analyze how skills are distributed across categories",
            },
        ],
        "note": "Try these queries with the /api/llm/query endpoint",
    }
