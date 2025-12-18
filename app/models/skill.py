"""
Skill model definitions.
"""

from pydantic import BaseModel, Field


class SkillBase(BaseModel):
    """Base skill model."""

    name: str = Field(..., min_length=1, max_length=50, description="Skill name")
    category: str = Field(..., min_length=1, max_length=50, description="Skill category (e.g., Programming, Design)")


class SkillCreate(SkillBase):
    """Model for creating a new skill."""

    pass


class Skill(SkillBase):
    """Complete skill model."""

    skill_id: str = Field(..., description="Unique skill identifier")
    user_count: int = Field(0, ge=0, description="Number of users with this skill")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
