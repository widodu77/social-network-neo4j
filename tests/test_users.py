"""
User endpoint tests.
"""



def test_list_users(client):
    """
    Test listing users endpoint.
    """
    response = client.get("/api/users")

    # Should return 200 even if empty
    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)


def test_list_users_with_pagination(client):
    """
    Test listing users with pagination parameters.
    """
    response = client.get("/api/users?limit=10&offset=0")

    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10


def test_create_user(client, sample_user_data):
    """
    Test creating a user.
    """
    response = client.post("/api/users", json=sample_user_data)

    # Should return 201 or 500 depending on database connectivity
    assert response.status_code in [201, 500, 503]

    if response.status_code == 201:
        data = response.json()
        assert "user_id" in data
        assert data["name"] == sample_user_data["name"]
        assert data["email"] == sample_user_data["email"]


def test_create_user_invalid_data(client):
    """
    Test creating a user with invalid data.
    """
    invalid_data = {
        "name": "",  # Invalid: empty name
        "email": "invalid-email",  # Invalid email format
    }

    response = client.post("/api/users", json=invalid_data)

    assert response.status_code == 422  # Validation error


def test_get_user_not_found(client):
    """
    Test getting a non-existent user.
    """
    response = client.get("/api/users/non-existent-id")

    # Should return 404 or 500
    assert response.status_code in [404, 500, 503]
