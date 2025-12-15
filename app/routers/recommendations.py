"""
Recommendation endpoints.
"""
from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.models.recommendation import FriendRecommendation, JobRecommendation, PersonSuggestion
from app.services.recommendation_service import RecommendationService

router = APIRouter()
recommendation_service = RecommendationService()


@router.get("/users/{user_id}/recommendations/friends", response_model=List[FriendRecommendation])
async def get_friend_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations"),
):
    """
    Get friend recommendations based on mutual connections and common skills.

    This endpoint uses graph traversal to find potential connections:
    - Finds friends of friends (2nd degree connections)
    - Ranks by number of mutual connections
    - Considers common skills as additional signal

    Args:
        user_id: User ID
        limit: Maximum number of recommendations

    Returns:
        List of friend recommendations
    """
    try:
        recommendations = recommendation_service.get_friend_recommendations(user_id, limit)
        if not recommendations:
            return []
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/users/{user_id}/recommendations/jobs", response_model=List[JobRecommendation])
async def get_job_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations"),
):
    """
    Get job recommendations based on user skills.

    This endpoint analyzes the user's skill graph:
    - Matches user skills with job requirements
    - Finds companies where similar professionals work
    - Calculates skill match percentage

    Args:
        user_id: User ID
        limit: Maximum number of recommendations

    Returns:
        List of job recommendations
    """
    try:
        recommendations = recommendation_service.get_job_recommendations(user_id, limit)
        if not recommendations:
            return []
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/users/{user_id}/suggestions/people", response_model=List[PersonSuggestion])
async def get_people_suggestions(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
):
    """
    Get "people you may know" suggestions.

    This endpoint combines multiple graph signals:
    - Mutual connections (friends of friends)
    - Common skills
    - Same company
    - Connection path length

    The scoring algorithm weighs these factors to provide the most relevant suggestions.

    Args:
        user_id: User ID
        limit: Maximum number of suggestions

    Returns:
        List of person suggestions
    """
    try:
        suggestions = recommendation_service.get_people_suggestions(user_id, limit)
        if not suggestions:
            return []
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
