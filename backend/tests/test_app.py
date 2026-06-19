"""Tests for FastAPI app initialization and health check."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_docs_available():
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/auth/register" in schema["paths"]
    assert "/api/v1/auth/login" in schema["paths"]
    assert "/api/v1/dashboard" in schema["paths"]
    assert "/api/v1/experiences" in schema["paths"]
    assert "/api/v1/interviews/start" in schema["paths"]


def test_protected_route_without_auth():
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 403  # No bearer token


def test_protected_route_with_invalid_token():
    response = client.get(
        "/api/v1/dashboard",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401
