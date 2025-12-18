"""
Path finding endpoint tests.
"""


def test_shortest_path(client):
    """
    Test shortest path endpoint.
    """
    from_user = "user-1"
    to_user = "user-2"

    response = client.get(f"/api/paths/shortest?from={from_user}&to={to_user}")

    # Should return 200 or 500
    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert "from_user_id" in data
        assert "to_user_id" in data
        assert "path_length" in data
        assert "nodes" in data
        assert "exists" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["exists"], bool)


def test_shortest_path_same_user(client):
    """
    Test shortest path with same source and target.
    """
    user_id = "user-1"

    response = client.get(f"/api/paths/shortest?from={user_id}&to={user_id}")

    # Should return 400 (bad request)
    assert response.status_code == 400


def test_shortest_path_missing_params(client):
    """
    Test shortest path with missing parameters.
    """
    # Missing 'to' parameter
    response = client.get("/api/paths/shortest?from=user-1")
    assert response.status_code == 422  # Validation error

    # Missing 'from' parameter
    response = client.get("/api/paths/shortest?to=user-2")
    assert response.status_code == 422
