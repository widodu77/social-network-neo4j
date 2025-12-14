"""
User model definitions.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """Base user model with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    title: Optional[str] = Field(None, max_length=100, description="Job title")
    location: Optional[str] = Field(None, max_length=100, description="Location")
    bio: Optional[str] = Field(None, max_length=500, description="Short biography")


class UserCreate(UserBase):
    """Model for creating a new user."""

    skills: Optional[List[str]] = Field(default_factory=list, description="List of skill names")
    company: Optional[str] = Field(None, description="Company name")


class User(UserBase):
    """Complete user model."""

    user_id: str = Field(..., description="Unique user identifier")
    connection_count: Optional[int] = Field(0, description="Number of connections")
    skill_count: Optional[int] = Field(0, description="Number of skills")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserResponse(BaseModel):
    """User response model with relationships."""

    user_id: str
    name: str
    email: str
    title: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    company: Optional[str] = None
    connections: List[str] = Field(default_factory=list, description="List of connected user IDs")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
