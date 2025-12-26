"""Agent Authentication Service with OTP-based password reset."""
import random
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.agent import Agent
from app.models.agent_otp import AgentOTP
from app.schemas.agent_auth_schema import (
    AgentLoginRequest,
    AgentLoginResponse,
    AgentRegisterRequest,
    AgentRegisterResponse,
    AgentResetPasswordRequest,
    AgentUpdateRequest,
    AgentResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
)
from app.services.email_service import send_otp_email, send_password_reset_success_email
from app.utils.logging import logger
from app.utils.response import error_response, internal_server_error, success_response


def generate_otp(length: int = 4) -> str:
    """Generate a random numeric OTP of specified length."""
    return "".join(random.choices(string.digits, k=length))


def generate_reset_token() -> str:
    """Generate a secure random reset token."""
    return secrets.token_urlsafe(32)


def mask_email(email: str) -> str:
    """Mask email address for privacy (e.g., a***@example.com)."""
    try:
        local, domain = email.split("@")
        if len(local) <= 2:
            masked_local = local[0] + "***"
        else:
            masked_local = local[0] + "***" + local[-1]
        return f"{masked_local}@{domain}"
    except Exception:
        return "***@***.***"


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


# ============== OTP-Based Password Reset Functions ==============


async def request_password_reset_otp(
    db: AsyncSession, request_data: ForgotPasswordRequest
) -> Optional[dict]:
    """
    Step 1: Request OTP for password reset.
    - Verify email exists in database
    - Generate 4-digit OTP
    - Store OTP with expiration
    - Send OTP to registered email
    """
    try:
        # Find agent by email (case-insensitive)
        stmt = select(Agent).where(
            func.lower(Agent.email) == func.lower(request_data.email)
        )
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            logger.warning(
                "Password reset OTP requested for non-existent email: %s",
                request_data.email,
            )
            return error_response(
                status_code=404,
                message="No account found with this email address",
            )

        # Invalidate any existing OTPs for this agent
        await db.execute(
            update(AgentOTP)
            .where(AgentOTP.agent_id == agent.id, AgentOTP.is_used == False)
            .values(is_used=True)
        )

        # Generate new OTP
        otp_code = generate_otp(settings.OTP_LENGTH)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )

        # Store OTP in database
        otp_record = AgentOTP(
            agent_id=agent.id,
            email=agent.email,
            otp_code=otp_code,
            expires_at=expires_at,
            is_verified=False,
            is_used=False,
        )
        db.add(otp_record)
        await db.commit()

        # Send OTP via email
        email_sent = await send_otp_email(
            to_email=agent.email,
            otp_code=otp_code,
            agent_name=agent.name,
        )

        if not email_sent:
            logger.error("Failed to send OTP email to: %s", agent.email)
            return error_response(
                status_code=500,
                message="Failed to send OTP email. Please try again later.",
            )

        response = ForgotPasswordResponse(
            email=mask_email(agent.email),
            message="OTP has been sent to your registered email address",
            otp_expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
        )

        logger.info("Password reset OTP sent to: %s", agent.email)

        return success_response(
            data=response.model_dump(),
            message="OTP sent successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Password reset OTP request error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Failed to process password reset request: {str(e)}")


async def verify_password_reset_otp(
    db: AsyncSession, verify_data: VerifyOTPRequest
) -> Optional[dict]:
    """
    Step 2: Verify the OTP.
    - Validate OTP against stored value
    - Check OTP expiration
    - Generate reset token on success
    """
    try:
        # Find agent by email
        stmt = select(Agent).where(
            func.lower(Agent.email) == func.lower(verify_data.email)
        )
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            return error_response(
                status_code=404,
                message="No account found with this email address",
            )

        # Find valid OTP for this agent
        stmt = (
            select(AgentOTP)
            .where(
                AgentOTP.agent_id == agent.id,
                AgentOTP.otp_code == verify_data.otp,
                AgentOTP.is_used == False,
                AgentOTP.is_verified == False,
            )
            .order_by(AgentOTP.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        otp_record = result.scalar_one_or_none()

        if not otp_record:
            logger.warning(
                "Invalid OTP attempt for email: %s", verify_data.email
            )
            return error_response(
                status_code=400,
                message="Invalid OTP. Please check and try again.",
            )

        # Check if OTP has expired
        if datetime.now(timezone.utc) > otp_record.expires_at:
            logger.warning("Expired OTP used for email: %s", verify_data.email)
            return error_response(
                status_code=400,
                message="OTP has expired. Please request a new one.",
            )

        # Generate reset token
        reset_token = generate_reset_token()

        # Mark OTP as verified and store reset token
        otp_record.is_verified = True
        otp_record.reset_token = reset_token
        # Extend expiration for reset token (additional 10 minutes for password reset)
        otp_record.expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )
        await db.commit()

        response = VerifyOTPResponse(
            email=agent.email,
            reset_token=reset_token,
            message="OTP verified successfully. Use the reset token to set your new password.",
        )

        logger.info("OTP verified successfully for: %s", agent.email)

        return success_response(
            data=response.model_dump(),
            message="OTP verified successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("OTP verification error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Failed to verify OTP: {str(e)}")


async def reset_agent_password(
    db: AsyncSession, reset_data: AgentResetPasswordRequest
) -> Optional[dict]:
    """
    Step 3: Reset agent password using verified reset token.
    - Validate reset token
    - Update password in database
    - Invalidate reset token
    """
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

        # Find valid reset token
        stmt = (
            select(AgentOTP)
            .where(
                AgentOTP.agent_id == agent.id,
                AgentOTP.reset_token == reset_data.reset_token,
                AgentOTP.is_verified == True,
                AgentOTP.is_used == False,
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        otp_record = result.scalar_one_or_none()

        if not otp_record:
            logger.warning(
                "Invalid reset token used for email: %s", reset_data.email
            )
            return error_response(
                status_code=400,
                message="Invalid or expired reset token. Please request a new OTP.",
            )

        # Check if reset token has expired
        if datetime.now(timezone.utc) > otp_record.expires_at:
            logger.warning("Expired reset token used for email: %s", reset_data.email)
            return error_response(
                status_code=400,
                message="Reset token has expired. Please request a new OTP.",
            )

        # Update password
        agent.password_hash = hash_password(reset_data.new_password)
        
        # Mark OTP as used (invalidate)
        otp_record.is_used = True
        
        await db.commit()
        await db.refresh(agent)

        # Send success email (non-blocking - don't fail if email fails)
        try:
            await send_password_reset_success_email(agent.email, agent.name)
        except Exception as email_error:
            logger.warning(
                "Failed to send password reset success email: %s", str(email_error)
            )

        logger.info("Agent password reset successful for: %s", agent.email)

        # Clean up old OTPs for this agent (keep DB clean)
        await db.execute(
            delete(AgentOTP).where(
                AgentOTP.agent_id == agent.id,
                AgentOTP.is_used == True,
            )
        )
        await db.commit()

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


# ============== Agent Management Functions ==============


async def get_agents_list(db: AsyncSession) -> Optional[dict]:
    """Get list of all agents."""
    try:
        stmt = select(Agent).order_by(Agent.created_at.desc())
        result = await db.execute(stmt)
        agents = result.scalars().all()

        agent_responses = []
        for agent in agents:
            agent_response = AgentResponse(
                id=str(agent.id),
                email=agent.email,
                username=agent.username,
                name=agent.name,
                contact_no=agent.contact_no,
                logo_url=agent.logo_url,
                city=agent.city,
                state=agent.state,
                experience=agent.experience,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
            )
            agent_responses.append(agent_response)

        return success_response(
            data=agent_responses,
            message="Agents retrieved successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Get agents list error: %s", str(e), exc_info=True)
        return internal_server_error(f"Failed to retrieve agents: {str(e)}")


async def get_agent_by_id(db: AsyncSession, agent_id: str) -> Optional[dict]:
    """Get a specific agent by ID."""
    try:
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            return error_response(
                status_code=404,
                message="Agent not found",
            )

        agent_response = AgentResponse(
            id=str(agent.id),
            email=agent.email,
            username=agent.username,
            name=agent.name,
            contact_no=agent.contact_no,
            logo_url=agent.logo_url,
            city=agent.city,
            state=agent.state,
            experience=agent.experience,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )

        return success_response(
            data=agent_response.model_dump(),
            message="Agent retrieved successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Get agent by ID error: %s", str(e), exc_info=True)
        return internal_server_error(f"Failed to retrieve agent: {str(e)}")


async def update_agent(
    db: AsyncSession, agent_id: str, update_data: AgentUpdateRequest
) -> Optional[dict]:
    """Update agent information."""
    try:
        # Check if agent exists
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            return error_response(
                status_code=404,
                message="Agent not found",
            )

        # Check for email and username uniqueness if they are being updated
        if update_data.email is not None or update_data.username is not None:
            conditions = []
            if update_data.email is not None:
                conditions.append(func.lower(Agent.email) == func.lower(update_data.email))
            if update_data.username is not None:
                conditions.append(func.lower(Agent.username) == func.lower(update_data.username))
            
            if conditions:
                stmt = select(Agent).where(
                    or_(*conditions),
                    Agent.id != agent_id  # Exclude current agent from check
                )
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    if update_data.email is not None and existing.email.lower() == update_data.email.lower():
                        return error_response(
                            status_code=400,
                            message="Email already exists",
                        )
                    if update_data.username is not None and existing.username.lower() == update_data.username.lower():
                        return error_response(
                            status_code=400,
                            message="Username already exists",
                        )

        # Update only provided fields
        update_values = {}
        if update_data.email is not None:
            update_values["email"] = update_data.email
        if update_data.username is not None:
            update_values["username"] = update_data.username
        if update_data.name is not None:
            update_values["name"] = update_data.name
        if update_data.contact_no is not None:
            update_values["contact_no"] = update_data.contact_no
        if update_data.logo_url is not None:
            update_values["logo_url"] = update_data.logo_url
        if update_data.city is not None:
            update_values["city"] = update_data.city
        if update_data.state is not None:
            update_values["state"] = update_data.state
        if update_data.experience is not None:
            update_values["experience"] = update_data.experience

        if not update_values:
            return error_response(
                status_code=400,
                message="No fields to update",
            )

        # Apply updates
        stmt = (
            update(Agent)
            .where(Agent.id == agent_id)
            .values(**update_values)
            .returning(Agent)
        )
        result = await db.execute(stmt)
        await db.commit()
        updated_agent = result.scalar_one()

        agent_response = AgentResponse(
            id=str(updated_agent.id),
            email=updated_agent.email,
            username=updated_agent.username,
            name=updated_agent.name,
            contact_no=updated_agent.contact_no,
            logo_url=updated_agent.logo_url,
            city=updated_agent.city,
            state=updated_agent.state,
            experience=updated_agent.experience,
            created_at=updated_agent.created_at,
            updated_at=updated_agent.updated_at,
        )

        logger.info("Agent updated successfully: %s", agent_id)

        return success_response(
            data=agent_response.model_dump(),
            message="Agent updated successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Update agent error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Failed to update agent: {str(e)}")


async def delete_agent(db: AsyncSession, agent_id: str) -> Optional[dict]:
    """Delete an agent by ID."""
    try:
        # Check if agent exists
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            return error_response(
                status_code=404,
                message="Agent not found",
            )

        # Delete agent
        stmt = delete(Agent).where(Agent.id == agent_id)
        await db.execute(stmt)
        await db.commit()

        logger.info("Agent deleted successfully: %s", agent_id)

        return success_response(
            data={"agent_id": agent_id},
            message="Agent deleted successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Delete agent error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Failed to delete agent: {str(e)}")