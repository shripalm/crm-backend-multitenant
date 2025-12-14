from typing import Optional
import jwt
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.users import User
from app.models.roles import Role
from app.utils.logging import logger
from app.core.config import settings


async def get_current_user(
    token: Optional[str] = Header(None, description="Access Token"),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extract and validate the current user from JWT token using HS256.
    
    Uses the same SECRET_KEY and HS256 algorithm as the login endpoint.
    Loads user with roles and permissions using selectinload to prevent lazy loading errors.
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
        
    Returns:
        User object with roles and permissions eagerly loaded
        
    Raises:
        HTTPException: For authentication errors
    """
    if not token:
        logger.warning("Missing authentication token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decode JWT token using HS256 and SECRET_KEY (same as login)
        logger.debug("Decoding JWT token with HS256")
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        
        # Extract user_id from payload
        user_id = payload.get("user_id")
        if not user_id:
            logger.warning("JWT token missing user_id field")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Query user with roles and permissions eagerly loaded
        logger.debug(f"Loading user: {user_id}")
        result = await db.execute(
            select(User).options(
                selectinload(User.roles).selectinload(Role.permissions)
            ).where(
                User.id == user_id,
                User.active == True
            )
        )
        
        user = result.scalars().first()
        
        if not user:
            logger.warning(f"User not found or inactive: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Successfully authenticated user: {user.email}")
        return user
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )
