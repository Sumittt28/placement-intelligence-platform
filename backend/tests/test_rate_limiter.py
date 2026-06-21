"""Tests for rate limiting middleware."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.middleware import rate_limiter


def test_rate_limit_not_triggered_on_normal_use():
    """A single request should not be rate limited."""
    rate_limiter._requests.clear()
    rate_limiter._request_counter = 0
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_rate_limit_triggered_on_excessive_requests():
    """Exceeding the limit should return 429."""
    rate_limiter._requests.clear()
    rate_limiter._request_counter = 0
    client = TestClient(app)

    # Hammer the API beyond the public limit
    triggered = False
    for i in range(rate_limiter.RATE_LIMIT_MAX_PUBLIC + 5):
        response = client.get("/api/v1/dashboard")
        if response.status_code == 429:
            data = response.json()
            assert data["success"] is False
            assert "Rate limit exceeded" in data["error"]
            triggered = True
            break

    assert triggered, "Rate limiting did not trigger after exceeding max requests"


def test_rate_limiter_stale_key_cleanup():
    """Verify stale keys are cleaned up to prevent memory leak."""
    import time
    rate_limiter._requests.clear()
    rate_limiter._request_counter = 0

    # Add some stale entries
    old_time = time.time() - rate_limiter.RATE_LIMIT_WINDOW - 10
    rate_limiter._requests["stale-ip-1"] = [old_time]
    rate_limiter._requests["stale-ip-2"] = [old_time]
    rate_limiter._requests["fresh-ip"] = [time.time()]

    assert len(rate_limiter._requests) == 3

    rate_limiter._cleanup_all_stale_keys(time.time())

    assert "stale-ip-1" not in rate_limiter._requests
    assert "stale-ip-2" not in rate_limiter._requests
    assert "fresh-ip" in rate_limiter._requests
