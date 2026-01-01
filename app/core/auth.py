import jwt
import uuid
from typing import Optional, Any
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.admin_session import get_admin_db
from app.models.users import User
from app.models.roles import Role
from app.models.agent import Agent
from typing import Any
from app.utils.logging import logger
from app.core.config import settings


async def get_current_user(
    token: Optional[str] = Header(None, description="Access Token in 'token' header"),
    db: AsyncSession = Depends(get_db),
    admin_db: AsyncSession = Depends(get_admin_db)
) -> Any:
    """
    Extract and validate the current user from JWT token using settings.ALGORITHM.
    Strictly reads from 'token' header as per production hotfix requirements.
    Role-aware: Queries 'agents' table for AGENT role, 'users' table for ADMIN/other.
    """
    if not token:
        logger.warning("Missing 'token' header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required in 'token' header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract JWT from Bearer format if user accidentally provides it, 
    # but the requirement is to read the header directly.
    clean_token = token
    if token.lower().startswith("bearer "):
        clean_token = token[7:]
    
    try:
        # Decode JWT token using centralized SECRET_KEY and ALGORITHM
        payload = jwt.decode(
            clean_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False, "verify_iss": False}
        )
        
        logger.debug(f"JWT decoded successfully. Payload: {payload}")
        
        # Support both 'user_id' and role-specific keys for robustness
        user_id = payload.get("user_id") or payload.get("agent_id") or payload.get("admin_id")
        role = payload.get("role")
        
        # Infer role if missing but role-specific ID keys are present
        if not role:
            if "agent_id" in payload: role = "AGENT"
            elif "admin_id" in payload: role = "ADMIN"
        
        if not user_id:
            logger.warning("JWT token missing identity field (user_id/agent_id/admin_id)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing identity",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Cast to UUID to prevent DB type errors (Postgres UUID vs String)
        try:
            lookup_id = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        except ValueError:
            lookup_id = user_id

        # Identity Lookup based on Role
        if role == "AGENT":
            logger.debug(f"Role AGENT detected. Loading from agents table (admin_db): {lookup_id}")
            # Correct fix: query agents table using the admin_db session
            result = await admin_db.execute(select(Agent).where(Agent.id == lookup_id))
            user = result.scalars().first()
        else:
            # Default to User table in client DB as requested (ADMIN -> users table)
            logger.debug(f"Role {role} detected. Loading from users table (client_db): {lookup_id}")
            result = await db.execute(
                select(User).options(
                    selectinload(User.roles).selectinload(Role.permissions)
                ).where(
                    User.id == lookup_id,
                    User.active == True
                )
            )
            user = result.scalars().first()
        
        if not user:
            logger.warning(f"User/Agent not found or inactive: {lookup_id} (Role: {role})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Successfully authenticated {role}: {getattr(user, 'email', lookup_id)}")
        return user
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        # Logging exact error as requested for production debugging
        logger.error(f"JWT Decode Failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected authentication error: {str(e)}", exc_info=True)
        # Expose real error for debugging as requested
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication service error: {str(e)}"
        )
