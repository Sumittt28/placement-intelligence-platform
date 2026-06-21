"""
Integration tests for core user flows.
Tests the full API request/response cycle against the REAL Supabase database.
Run with: python -m pytest tests/test_integration.py -v
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import get_db, async_session
from app.core.security import create_access_token
import uuid


# Unique email per test run to avoid conflicts
RUN_ID = uuid.uuid4().hex[:8]


# Override back to REAL database (conftest overrides to SQLite)
async def real_get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
async def client():
    """Async HTTP test client — connects to REAL Supabase DB."""
    app.dependency_overrides[get_db] = real_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def unique_email():
    """Generate a unique email for each test."""
    return f"test_{RUN_ID}_{uuid.uuid4().hex[:6]}@test.com"


# ============================================================
# Auth Flow Tests
# ============================================================

class TestAuthFlow:
    """Test complete auth flow: register → login → get profile."""

    @pytest.mark.asyncio
    async def test_full_auth_flow(self, client: AsyncClient, unique_email: str):
        # 1. Register
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Integration Test User",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["user"]["email"] == unique_email
        token = data["data"]["access_token"]

        # 2. Login with same credentials
        r = await client.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "StrongPass123!",
        })
        assert r.status_code == 200
        assert r.json()["success"] is True

        # 3. Get profile with token
        r = await client.get("/api/v1/users/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert r.status_code == 200
        profile_data = r.json()["data"]
        assert profile_data["email"] == unique_email
        assert profile_data["profile"]["full_name"] == "Integration Test User"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, unique_email: str):
        # Register first time
        await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "First User",
        })

        # Register again — should fail
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Second User",
        })
        assert r.status_code == 409
        assert r.json()["success"] is False

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, unique_email: str):
        # Register
        await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Test User",
        })

        # Login with wrong password
        r = await client.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "WrongPassword!",
        })
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_route_no_token(self, client: AsyncClient):
        r = await client.get("/api/v1/dashboard")
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_protected_route_invalid_token(self, client: AsyncClient):
        r = await client.get("/api/v1/dashboard", headers={
            "Authorization": "Bearer invalid.token.here",
        })
        assert r.status_code == 401


# ============================================================
# Dashboard Flow Tests
# ============================================================

class TestDashboardFlow:
    """Test dashboard returns correct structure."""

    @pytest.mark.asyncio
    async def test_dashboard_structure(self, client: AsyncClient, unique_email: str):
        # Register and get token
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Dashboard Test User",
        })
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get dashboard
        r = await client.get("/api/v1/dashboard", headers=headers)
        assert r.status_code == 200
        data = r.json()["data"]

        # Verify structure
        assert "profile_summary" in data
        assert "stats" in data
        assert "recent_activity" in data
        assert "performance" in data
        assert "trends" in data

        # Verify stats are zeroed for new user
        assert data["stats"]["interviews_attempted"] == 0
        assert data["stats"]["ai_interviews_completed"] == 0

        # Verify profile summary
        assert data["profile_summary"]["full_name"] == "Dashboard Test User"


# ============================================================
# Company Flow Tests
# ============================================================

class TestCompanyFlow:
    """Test company listing and intelligence."""

    @pytest.mark.asyncio
    async def test_list_companies(self, client: AsyncClient, unique_email: str):
        # Register and get token
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Company Test User",
        })
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List companies
        r = await client.get("/api/v1/companies", headers=headers)
        assert r.status_code == 200
        companies = r.json()["data"]
        assert isinstance(companies, list)
        assert len(companies) > 0  # Seeded companies should exist

        # Verify company structure
        company = companies[0]
        assert "id" in company
        assert "name" in company
        assert "industry" in company

    @pytest.mark.asyncio
    async def test_search_companies(self, client: AsyncClient, unique_email: str):
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Search Test User",
        })
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Search for Google
        r = await client.get("/api/v1/companies?search=Google", headers=headers)
        assert r.status_code == 200
        companies = r.json()["data"]
        assert any("Google" in c["name"] for c in companies)

    @pytest.mark.asyncio
    async def test_company_intelligence(self, client: AsyncClient, unique_email: str):
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Intel Test User",
        })
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get companies first
        r = await client.get("/api/v1/companies", headers=headers)
        companies = r.json()["data"]
        company_id = companies[0]["id"]

        # Get intelligence
        r = await client.get(f"/api/v1/companies/{company_id}", headers=headers)
        assert r.status_code == 200
        intel = r.json()["data"]
        assert "company" in intel
        assert "analytics" in intel
        assert "frequently_asked_questions" in intel


# ============================================================
# Profile Update Flow Tests
# ============================================================

class TestProfileFlow:
    """Test profile update flow."""

    @pytest.mark.asyncio
    async def test_update_profile(self, client: AsyncClient, unique_email: str):
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Profile Test User",
        })
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update profile
        r = await client.put("/api/v1/users/me/profile", headers=headers, json={
            "full_name": "Updated Name",
            "batch": "2026",
            "graduation_year": 2026,
            "linkedin_url": "https://linkedin.com/in/test",
        })
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["profile"]["full_name"] == "Updated Name"
        assert data["profile"]["batch"] == "2026"
        assert data["profile"]["graduation_year"] == 2026


# ============================================================
# Weaknesses & Recommendations Flow Tests
# ============================================================

class TestIntelligenceFlow:
    """Test weaknesses and recommendations endpoints."""

    @pytest.mark.asyncio
    async def test_weaknesses_empty(self, client: AsyncClient, unique_email: str):
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Weakness Test User",
        })
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await client.get("/api/v1/weaknesses", headers=headers)
        assert r.status_code == 200
        assert r.json()["data"] == []

    @pytest.mark.asyncio
    async def test_readiness_new_user(self, client: AsyncClient, unique_email: str):
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Readiness Test User",
        })
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await client.get("/api/v1/readiness", headers=headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert "overall_readiness" in data


# ============================================================
# Search Flow Tests
# ============================================================

class TestSearchFlow:
    """Test knowledge base search."""

    @pytest.mark.asyncio
    async def test_search_returns_results(self, client: AsyncClient, unique_email: str):
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Search Test User",
        })
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await client.get("/api/v1/search?q=python", headers=headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert "query" in data
        assert "results" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_search_requires_query(self, client: AsyncClient, unique_email: str):
        r = await client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPass123!",
            "full_name": "Search Validation User",
        })
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Empty query should fail validation
        r = await client.get("/api/v1/search?q=", headers=headers)
        assert r.status_code == 422


# ============================================================
# Rate Limiting Tests (Live)
# ============================================================

class TestRateLimiting:
    """Test rate limiting works on live endpoints."""

    @pytest.mark.asyncio
    async def test_rate_limit_not_hit_on_normal_use(self, client: AsyncClient):
        """5 requests should be fine."""
        from app.middleware.rate_limiter import _requests
        _requests.clear()

        for _ in range(5):
            r = await client.get("/health")
            assert r.status_code == 200
