"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuth:
    async def test_register_success(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "StrongPass123!",
            "full_name": "Test User",
        })
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"] or "user" in data["data"]

    async def test_register_duplicate_email(self, client: AsyncClient):
        # Register first time
        await client.post("/api/v1/auth/register", json={
            "email": "duplicate@test.com",
            "password": "StrongPass123!",
            "full_name": "Test User",
        })
        # Register again with same email
        response = await client.post("/api/v1/auth/register", json={
            "email": "duplicate@test.com",
            "password": "StrongPass123!",
            "full_name": "Test User",
        })
        assert response.status_code == 409

    async def test_login_success(self, client: AsyncClient):
        # Register first
        await client.post("/api/v1/auth/register", json={
            "email": "logintest@test.com",
            "password": "StrongPass123!",
            "full_name": "Test User",
        })
        # Login
        response = await client.post("/api/v1/auth/login", json={
            "email": "logintest@test.com",
            "password": "StrongPass123!",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_login_wrong_password(self, client: AsyncClient):
        # Register
        await client.post("/api/v1/auth/register", json={
            "email": "wrongpass@test.com",
            "password": "StrongPass123!",
            "full_name": "Test User",
        })
        # Login with wrong password
        response = await client.post("/api/v1/auth/login", json={
            "email": "wrongpass@test.com",
            "password": "WrongPass!",
        })
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", json={
            "email": "noone@test.com",
            "password": "Pass123!",
        })
        assert response.status_code == 401
