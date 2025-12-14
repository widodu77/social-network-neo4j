"""
Recommendation model definitions.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class FriendRecommendation(BaseModel):
    """Friend recommendation model."""

    user_id: str = Field(..., description="Recommended user ID")
    name: str = Field(..., description="User name")
    title: Optional[str] = Field(None, description="Job title")
    mutual_connections: int = Field(..., ge=0, description="Number of mutual connections")
    common_skills: List[str] = Field(default_factory=list, description="Common skills")
    score: float = Field(..., ge=0, le=1, description="Recommendation score (0-1)")
    reason: str = Field(..., description="Reason for recommendation")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class JobRecommendation(BaseModel):
    """Job recommendation model."""

    job_id: str = Field(..., description="Job posting ID")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    matching_skills: List[str] = Field(default_factory=list, description="User's matching skills")
    skill_match_rate: float = Field(..., ge=0, le=1, description="Percentage of matching skills")
    score: float = Field(..., ge=0, le=1, description="Recommendation score (0-1)")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class PersonSuggestion(BaseModel):
    """People you may know suggestion model."""

    user_id: str = Field(..., description="Suggested user ID")
    name: str = Field(..., description="User name")
    title: Optional[str] = Field(None, description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    mutual_connections: int = Field(..., ge=0, description="Number of mutual connections")
    common_skills: int = Field(..., ge=0, description="Number of common skills")
    same_company: bool = Field(False, description="Works at the same company")
    connection_path_length: Optional[int] = Field(
        None, description="Shortest path length to this person"
    )
    score: float = Field(..., ge=0, le=1, description="Suggestion score (0-1)")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
