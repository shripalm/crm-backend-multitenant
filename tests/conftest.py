# tests/conftest.py
import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from sqlalchemy.ext.asyncio import AsyncSession
from tests.db.test_session import AsyncSessionLocal
from app.main import app  # your FastAPI app
from sqlalchemy import text
from httpx._transports.asgi import ASGITransport
from asgi_lifespan import LifespanManager


# -------------------------
# DB session fixture
# -------------------------
@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session

# -------------------------
# Async FastAPI test client
# -------------------------
# Async client fixture
@pytest.fixture
async def client(db_session):
    """
    Async test client for FastAPI using httpx + ASGITransport
    """
    transport = ASGITransport(app=app)  
    async with LifespanManager(app):
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver"
        ) as ac:
            yield ac

# -------------------------
# Override FastAPI dependencies
# -------------------------
from app.db.session import get_db  # adjust to your project

@pytest.fixture(autouse=True)
def override_get_db(db_session: AsyncSession):
    async def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()

# -------------------------------
# Fixtures for file content
@pytest.fixture
def sample_csv_content():
    return b"name,age\nAlice,30\nBob,25"

@pytest.fixture
def invalid_file_content():
    return b"\x00\x01\x02\x03\x04\x05"