from datetime import timedelta
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.agent import Agent
from app.schemas.agent_auth_schema import (
    AgentLoginRequest,
    AgentLoginResponse,
    AgentRegisterRequest,
    AgentRegisterResponse,
    AgentResetPasswordRequest,
)
from app.utils.logging import logger
from app.utils.response import error_response, internal_server_error, success_response


async def register_agent(
    db: AsyncSession, register_data: AgentRegisterRequest
) -> Optional[dict]:
    """Register a new agent."""

    try:
        stmt = select(Agent).where(
            or_(
                func.lower(Agent.email) == func.lower(register_data.email),
                func.lower(Agent.username) == func.lower(register_data.username),
            )
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return error_response(
                status_code=400,
                message="Agent with this email or username already exists",
            )

        agent = Agent(
            email=register_data.email,
            username=register_data.username,
            password_hash=hash_password(register_data.password),
            name=register_data.name,
            contact_no=register_data.contact_no,
            logo_url=register_data.logo_url,
            city=register_data.city,
            state=register_data.state,
            experience=register_data.experience,
        )

        db.add(agent)
        await db.commit()
        await db.refresh(agent)

        response = AgentRegisterResponse(
            agent_id=str(agent.id),
            email=agent.email,
            username=agent.username,
            name=agent.name,
        )

        return success_response(
            data=response.model_dump(),
            message="Agent registered successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Agent registration error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Agent registration failed: {str(e)}")


async def authenticate_agent(
    db: AsyncSession, login_data: AgentLoginRequest
) -> Optional[dict]:
    """Authenticate agent using email or username and password."""

    try:
        email_or_username = login_data.email_or_username.strip()

        stmt = select(Agent).where(
            or_(
                func.lower(Agent.email) == func.lower(email_or_username),
                func.lower(Agent.username) == func.lower(email_or_username),
            )
        )
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            logger.warning(
                "Agent login failed - not found: %s", email_or_username
            )
            return error_response(
                status_code=401,
                message="Invalid email/username or password",
            )

        if not verify_password(login_data.password, agent.password_hash):
            logger.warning(
                "Agent login failed - invalid password for: %s", agent.email
            )
            return error_response(
                status_code=401,
                message="Invalid email/username or password",
            )

        token_data = {
            "agent_id": str(agent.id),
            "email": agent.email,
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        response = AgentLoginResponse(
            access_token=access_token,
            token_type="bearer",
            agent_id=str(agent.id),
            email=agent.email,
            username=agent.username,
            name=agent.name,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        return success_response(
            data=response.model_dump(),
            message="Login successful",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Agent login error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Authentication failed: {str(e)}")


async def reset_agent_password(
    db: AsyncSession, reset_data: AgentResetPasswordRequest
) -> Optional[dict]:
    """Reset agent password using email, new_password and confirm_password."""

    try:
        # Validate passwords match
        if reset_data.new_password != reset_data.confirm_password:
            return error_response(
                status_code=400,
                message="Passwords do not match",
            )

        # Find agent by email (case-insensitive)
        stmt = select(Agent).where(
            func.lower(Agent.email) == func.lower(reset_data.email)
        )
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            logger.warning(
                "Agent password reset attempt for non-existent email: %s",
                reset_data.email,
            )
            return error_response(
                status_code=404,
                message="Agent with this email not found",
            )

        # Update password
        agent.password_hash = hash_password(reset_data.new_password)
        await db.commit()
        await db.refresh(agent)

        logger.info("Agent password reset successful for: %s", agent.email)

        return success_response(
            data={
                "email": agent.email,
                "message": "Password has been reset successfully",
            },
            message="Password reset successful",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Agent password reset error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Agent password reset failed: {str(e)}")
                                                                              