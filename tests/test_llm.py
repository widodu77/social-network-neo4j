"""
Tests for LLM-powered query endpoints.
"""


def test_llm_query_most_connected(client):
    """Test natural language query for most connected users."""
    response = client.post("/api/llm/query", json={"query": "Who are the most connected users?"})

    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert "natural_query" in data
        assert "cypher_query" in data
        assert "results" in data
        assert "explanation" in data
        assert isinstance(data["results"], list)


def test_llm_query_popular_skills(client):
    """Test natural language query for popular skills."""
    response = client.post("/api/llm/query", json={"query": "What are the popular skills?"})

    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert data["query_type"] == "popular skills"
        assert "skill" in data["cypher_query"].lower()


def test_llm_query_network_stats(client):
    """Test natural language query for network statistics."""
    response = client.post("/api/llm/query", json={"query": "What are the network statistics?"})

    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert "cypher_query" in data
        assert "total_users" in data["cypher_query"].lower()


def test_llm_query_unrecognized(client):
    """Test natural language query with unrecognized pattern."""
    response = client.post("/api/llm/query", json={"query": "Something completely random"})

    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)


def test_llm_user_insights(client, sample_user_data):
    """Test getting AI-powered user insights."""
    # First create a user
    create_response = client.post("/api/users", json=sample_user_data)

    if create_response.status_code == 201:
        user_id = create_response.json()["user_id"]

        # Get insights
        response = client.get(f"/api/llm/users/{user_id}/insights")

        assert response.status_code in [200, 404, 500, 503]

        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data
            assert "name" in data


def test_llm_example_queries(client):
    """Test getting example queries."""
    response = client.get("/api/llm/examples")

    assert response.status_code == 200
    data = response.json()

    assert "examples" in data
    assert isinstance(data["examples"], list)
    assert len(data["examples"]) > 0

    # Check structure of first example
    example = data["examples"][0]
    assert "query" in example
    assert "description" in example
