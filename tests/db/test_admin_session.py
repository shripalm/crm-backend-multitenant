import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import asyncio
import pytest

# Load environment
load_dotenv("test.env")

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from app.db.base_class import Base
from app.core.config import settings

# Ensure admin exists
TEST_ADMIN_URL = str(settings.DB_URLS.get("test_admin"))
if TEST_ADMIN_URL is None:
    raise RuntimeError("test_admin is missing in DB_URLS. Check test.env")

# Async engine and session
test_admin_engine = create_async_engine(TEST_ADMIN_URL, echo=True, future=True)
TestAdminSession = sessionmaker(
    test_admin_engine, class_=AsyncSession, expire_on_commit=False
)

# Fixture: setup/teardown database
@pytest.fixture(scope="session")
async def setup_test_admin():
    async with test_admin_engine.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_admin_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Fixture: provide a session per test
@pytest.fixture
async def admin_session(setup_test_admin):
    async with TestAdminSession() as session:
        async with session.begin():
            yield session
        await session.rollback()
