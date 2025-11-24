from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create admin engine
admin_engine = create_async_engine(
    str(settings.DB_URLS['admin']), 
    echo=False, 
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True
)

admin_session = sessionmaker(admin_engine, class_=AsyncSession, expire_on_commit=False)

async def get_admin_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an admin database session"""
    async with admin_session() as session:
        try:
            yield session
        finally:
            await session.close()