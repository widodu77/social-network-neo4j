"""
Company model definitions.
"""

from typing import Optional
from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    """Base company model."""

    name: str = Field(..., min_length=1, max_length=100, description="Company name")
    industry: Optional[str] = Field(None, max_length=50, description="Industry sector")
    location: Optional[str] = Field(None, max_length=100, description="Company location")
    size: Optional[str] = Field(None, description="Company size (e.g., 1-10, 11-50, 51-200, 201-500, 500+)")


class CompanyCreate(CompanyBase):
    """Model for creating a new company."""

    pass


class Company(CompanyBase):
    """Complete company model."""

    company_id: str = Field(..., description="Unique company identifier")
    employee_count: int = Field(0, ge=0, description="Number of employees in the network")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
