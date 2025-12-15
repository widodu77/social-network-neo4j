"""
Health check endpoint tests.
"""


def test_health_check(client):
    """
    Test the health check endpoint.
    """
    response = client.get("/health")

    # Should return 200 or 503 depending on database connectivity
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert data["status"] == "healthy"


def test_root_endpoint(client):
    """
    Test the root endpoint.
    """
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["version"] == "1.0.0"
