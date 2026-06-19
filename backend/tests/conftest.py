"""
Test configuration and fixtures for the Placement Intelligence Platform.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.session import Base
from app.main import app
from app.db.session import get_db
from app.core.security import create_access_token


# Use SQLite in-memory for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def student_token():
    """JWT token for a test student user."""
    return create_access_token({
        "sub": "test-user-id-123",
        "email": "student@test.com",
        "role": "student",
    })


@pytest.fixture
def admin_token():
    """JWT token for a test admin user."""
    return create_access_token({
        "sub": "admin-user-id-456",
        "email": "admin@test.com",
        "role": "admin",
    })


@pytest.fixture
def auth_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
