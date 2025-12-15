"""
Pytest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing.
    """
    return {
        "name": "Test User",
        "email": "test@example.com",
        "title": "Software Engineer",
        "location": "San Francisco, CA",
        "bio": "Test bio",
        "skills": ["Python", "FastAPI", "Neo4j"],
        "company": "TechCorp",
    }
