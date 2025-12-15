"""
Path finding endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.path import ShortestPath
from app.services.path_service import PathService

router = APIRouter()
path_service = PathService()


@router.get("/paths/shortest", response_model=ShortestPath)
async def find_shortest_path(
    from_user: str = Query(..., alias="from", description="Starting user ID"),
    to_user: str = Query(..., alias="to", description="Target user ID"),
):
    """
    Find the shortest path between two professionals in the network.

    This endpoint uses Neo4j's shortestPath algorithm to find the
    minimum number of connections between two users.

    Use cases:
    - Determine degree of separation between professionals
    - Find introduction paths
    - Analyze network connectivity

    Args:
        from_user: Starting user ID
        to_user: Target user ID

    Returns:
        Shortest path information including all intermediate nodes
    """
    if from_user == to_user:
        raise HTTPException(
            status_code=400, detail="Source and target users must be different"
        )

    try:
        return path_service.find_shortest_path(from_user, to_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
