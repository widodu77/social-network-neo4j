"""
User management endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.models.user import UserCreate, User, UserResponse
from app.services.user_service import UserService

router = APIRouter()
user_service = UserService()


@router.post("/users", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    """
    Create a new user.

    Args:
        user: User creation data

    Returns:
        Created user
    """
    try:
        return user_service.create_user(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Get user by ID with full details.

    Args:
        user_id: User ID

    Returns:
        User details
    """
    try:
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/users", response_model=List[User])
async def list_users(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
):
    """
    List all users with pagination.

    Args:
        limit: Maximum number of users to return
        offset: Number of users to skip

    Returns:
        List of users
    """
    try:
        return user_service.list_users(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
