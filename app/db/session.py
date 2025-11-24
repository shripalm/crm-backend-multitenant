from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# default engine (not used when middleware provides per-request engine)
default_engine = create_async_engine(str(settings.DB_URLS['default']), echo=False, future=True)
default_session = sessionmaker(default_engine, class_=AsyncSession, expire_on_commit=False)

# Backwards-compatible exports used elsewhere in the codebase
async_engine = default_engine
async_session = default_session


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an AsyncSession.

    If `request.state.async_session` exists (set by middleware), use that per-request sessionmaker.
    Otherwise fall back to the default session.
    """
    session_maker = None
    if request is not None and hasattr(request.state, "async_session") and request.state.async_session is not None:
        session_maker = request.state.async_session
    else:
        session_maker = default_session

    async with session_maker() as session:
        yield session
