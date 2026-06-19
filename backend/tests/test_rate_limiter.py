"""Tests for rate limiting middleware."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.middleware import rate_limiter


client = TestClient(app)


def test_rate_limit_not_triggered_on_normal_use():
    """A single request should not be rate limited."""
    # Reset state
    rate_limiter._requests.clear()
    response = client.get("/health")
    assert response.status_code == 200


def test_rate_limit_triggered_on_excessive_requests():
    """Exceeding the limit should return 429."""
    rate_limiter._requests.clear()

    # Hammer the API beyond the public limit
    for i in range(rate_limiter.RATE_LIMIT_MAX_PUBLIC + 5):
        response = client.get("/api/v1/dashboard")
        if response.status_code == 429:
            assert "Rate limit exceeded" in response.json().get("detail", "")
            return

    # If we got here, rate limiting didn't trigger (shouldn't happen)
    pytest.fail("Rate limiting did not trigger after exceeding max requests")
