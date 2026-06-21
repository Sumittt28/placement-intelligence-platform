"""
Test configuration and fixtures for the Placement Intelligence Platform.

Strategy:
- Unit tests (schemas, security, AI service interfaces) run WITHOUT a database.
- Integration tests (auth, app endpoints) require a database fixture explicitly.
- SQLite is used for tests but with type overrides for PostgreSQL-specific columns.
"""
import pytest
import asyncio
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event, String, Text, Float, Integer, Boolean, Date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.types import TypeDecorator, JSON
from app.db.session import Base
from app.main import app
from app.db.session import get_db
from app.core.security import create_access_token

# ============================================================
# SQLite-compatible type overrides for PostgreSQL types
# ============================================================
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB


# Override PostgreSQL types for SQLite compatibility at table creation time
@event.listens_for(Base.metadata, "column_reflect")
def _column_reflect(inspector, table, column_info):
    pass


# Monkey-patch the column types for SQLite testing
_original_uuid_impl = PG_UUID.__init__


# ============================================================
# Test Database Setup
# ============================================================
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    """Create tables and provide a database session for integration tests.
    Tests that need a DB should explicitly request this fixture."""
    # Override PostgreSQL types for SQLite
    from sqlalchemy.dialects.postgresql import UUID, JSONB
    from sqlalchemy import String, JSON

    # Create tables with type adaptation
    async with test_engine.begin() as conn:
        # We need to create tables with SQLite-compatible types
        # Use compile-time type adaptation
        await conn.run_sync(_create_tables_sqlite)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def _create_tables_sqlite(conn):
    """Create tables with SQLite-compatible types."""
    from sqlalchemy.dialects.postgresql import UUID, JSONB

    # Temporarily replace PostgreSQL types with SQLite-compatible ones
    original_types = {}
    for table in Base.metadata.tables.values():
        for col in table.columns:
            if isinstance(col.type, UUID):
                original_types[(table.name, col.name)] = col.type
                col.type = String(36)
            elif isinstance(col.type, JSONB):
                original_types[(table.name, col.name)] = col.type
                col.type = JSON()

    # Create tables
    Base.metadata.create_all(conn)

    # Restore original types
    for (table_name, col_name), orig_type in original_types.items():
        table = Base.metadata.tables[table_name]
        table.columns[col_name].type = orig_type


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
async def client(db_session):
    """Async HTTP test client (requires db_session)."""
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
