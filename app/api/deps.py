"""
API dependencies for FastAPI routes.

Provides common dependencies like database sessions that can be
imported across different API routers.
"""

from typing import AsyncGenerator, Any


from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db as get_db_session
from app.core.auth import get_current_user
from app.models.users import User

async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Database dependency for API routes.
    
    This is a wrapper around the session.get_db function to provide
    a consistent import path for API dependencies.
    """
    async for session in get_db_session(request):
        yield session

async def get_current_agent(
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Dependency to ensure the current user has the 'AGENT' role.
    Handles both Agent models (direct lookup) and User models (via roles).
    """
    from app.models.agent import Agent
    
    # If the identity lookup already returned an Agent model, we're good
    if isinstance(current_user, Agent):
        return current_user
        
    # Otherwise, check if the User model has the 'AGENT' role
    is_agent = any(role.name == "AGENT" for role in current_user.roles)
    
    if not is_agent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: User does not have AGENT role"
        )
    
    return current_user
