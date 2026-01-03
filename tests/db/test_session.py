# tests/test_session.py
import os
import json
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Load test environment variables
ENV_FILE = os.getenv("ENV_FILE", "test.env")
load_dotenv(ENV_FILE)

# Load test DB URL
DB_URLS = json.loads(os.environ.get("DB_URLS", "{}"))
TEST_DB_URL = DB_URLS.get("test_db")

# Create async engine for test DB
engine = create_async_engine(TEST_DB_URL, echo=False, poolclass=NullPool)

# Create sessionmaker
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)
