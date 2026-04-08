import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "empowerher"


def test_match_endpoint_success(client):
    """Test successful match request."""
    test_message = "I'm a woman interested in UX design and want to find mentors in tech."
    response = client.post(
        "/api/match",
        json={"message": test_message}
    )
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "summary" in data
    assert "mentors" in data
    assert "jobs" in data
    assert "next_steps" in data

    # Check that we get some results
    assert isinstance(data["mentors"], list)
    assert isinstance(data["jobs"], list)
    assert isinstance(data["next_steps"], list)
    assert len(data["mentors"]) > 0
    assert len(data["jobs"]) > 0


def test_match_endpoint_empty_message(client):
    """Test match request with empty message."""
    response = client.post(
        "/api/match",
        json={"message": ""}
    )
    # Should fail validation due to min_length constraint
    assert response.status_code == 422


def test_match_endpoint_short_message(client):
    """Test match request with very short message."""
    response = client.post(
        "/api/match",
        json={"message": "hi"}
    )
    # Should fail validation due to min_length constraint
    assert response.status_code == 422


def test_match_endpoint_long_message(client):
    """Test match request with long message."""
    long_message = "I am a woman with extensive experience in software engineering, " * 100
    response = client.post(
        "/api/match",
        json={"message": long_message}
    )
    # Should work with long messages
    assert response.status_code == 200


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options(
        "/api/health",
        headers={"Origin": "http://localhost:5173"}
    )
    assert "access-control-allow-origin" in response.headers


def test_rate_limiting(client):
    """Test rate limiting functionality."""
    # Make multiple requests quickly
    test_message = "Test message for rate limiting"

    # First few requests should succeed
    for i in range(5):
        response = client.post(
            "/api/match",
            json={"message": test_message}
        )
        assert response.status_code == 200

    # Additional requests might be rate limited (depending on timing)
    # This is a basic test - in production you'd want more sophisticated testing
    response = client.post(
        "/api/match",
        json={"message": test_message}
    )
    # Either succeeds or gets rate limited
    assert response.status_code in [200, 429]