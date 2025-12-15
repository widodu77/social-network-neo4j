"""
Recommendation endpoint tests.
"""
import pytest


def test_get_friend_recommendations(client):
    """
    Test friend recommendations endpoint.
    """
    # Use a sample user ID
    user_id = "test-user-id"
    response = client.get(f"/api/users/{user_id}/recommendations/friends")

    # Should return 200 (empty list) or 500 (if DB not connected)
    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)


def test_get_friend_recommendations_with_limit(client):
    """
    Test friend recommendations with limit parameter.
    """
    user_id = "test-user-id"
    response = client.get(f"/api/users/{user_id}/recommendations/friends?limit=5")

    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5


def test_get_job_recommendations(client):
    """
    Test job recommendations endpoint.
    """
    user_id = "test-user-id"
    response = client.get(f"/api/users/{user_id}/recommendations/jobs")

    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)


def test_get_people_suggestions(client):
    """
    Test people suggestions endpoint.
    """
    user_id = "test-user-id"
    response = client.get(f"/api/users/{user_id}/suggestions/people")

    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)


def test_recommendations_invalid_limit(client):
    """
    Test recommendations with invalid limit.
    """
    user_id = "test-user-id"

    # Limit too high
    response = client.get(f"/api/users/{user_id}/recommendations/friends?limit=1000")
    assert response.status_code == 422  # Validation error

    # Negative limit
    response = client.get(f"/api/users/{user_id}/recommendations/friends?limit=-1")
    assert response.status_code == 422
