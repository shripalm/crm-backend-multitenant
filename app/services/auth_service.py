"""User Authentication Service with OTP-based password reset."""
import random
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.users import User
from app.models.user_otp import UserOTP
from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
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


async def authenticate_user(
    db: AsyncSession, login_data: LoginRequest
) -> Optional[dict]:
    """Authenticate user with email/username and password."""

    try:
        email_or_username = login_data.email_or_username.strip()

        stmt = select(User).where(
            or_(
                func.lower(User.email) == func.lower(email_or_username),
                func.lower(User.full_name) == func.lower(email_or_username),
            )
        )

        result = await db.execute(stmt)
        user = result.unique().scalar_one_or_none()

        if not user:
            logger.warning(
                "User login failed - user not found: %s", email_or_username
            )
            return error_response(
                status_code=401,
                message="Invalid email/username or password",
            )

        if not user.active:
            logger.warning("User login failed - user inactive: %s", user.email)
            return error_response(
                status_code=403,
                message="Account is inactive. Please contact administrator.",
            )

        if not verify_password(login_data.password, user.password_hash):
            logger.warning(
                "User login failed - invalid password for user: %s", user.email
            )
            return error_response(
                status_code=401,
                message="Invalid email/username or password",
            )

        # Update last login time
        user.last_login = func.now()
        await db.commit()

        token_data = {
            "user_id": user.id,
            "email": user.email,
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        login_response = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        logger.info("User logged in successfully: %s", user.email)

        return success_response(
            data=login_response.model_dump(),
            message="Login successful",
        )

    except Exception as e:  # pragma: no cover
        logger.error("User login error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Authentication failed: {str(e)}")


async def verify_user_token(db: AsyncSession, user_id: str) -> Optional[User]:
    """Verify user exists and is active by user_id from token."""
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.unique().scalar_one_or_none()

        if user and user.active:
            return user
        return None

    except Exception as e:
        logger.error("Token verification error: %s", str(e))
        return None


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
        # Find user by email (case-insensitive)
        stmt = select(User).where(
            func.lower(User.email) == func.lower(request_data.email)
        )
        result = await db.execute(stmt)
        user = result.unique().scalar_one_or_none()

        if not user:
            logger.warning(
                "Password reset OTP requested for non-existent email: %s",
                request_data.email,
            )
            return error_response(
                status_code=404,
                message="No account found with this email address",
            )

        if not user.active:
            return error_response(
                status_code=403,
                message="Account is inactive. Please contact administrator.",
            )

        # Invalidate any existing OTPs for this user
        await db.execute(
            update(UserOTP)
            .where(UserOTP.user_id == user.id, UserOTP.is_used == False)
            .values(is_used=True)
        )

        # Generate new OTP
        otp_code = generate_otp(settings.OTP_LENGTH)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )

        # Store OTP in database
        otp_record = UserOTP(
            user_id=user.id,
            email=user.email,
            otp_code=otp_code,
            expires_at=expires_at,
            is_verified=False,
            is_used=False,
        )
        db.add(otp_record)
        await db.commit()

        # Send OTP via email
        email_sent = await send_otp_email(
            to_email=user.email,
            otp_code=otp_code,
            agent_name=user.full_name, # Reuse param name
        )

        if not email_sent:
            logger.error("Failed to send OTP email to: %s", user.email)
            return error_response(
                status_code=500,
                message="Failed to send OTP email. Please try again later.",
            )

        response = ForgotPasswordResponse(
            email=mask_email(user.email),
            message="OTP has been sent to your registered email address",
            otp_expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
        )

        logger.info("Password reset OTP sent to user: %s", user.email)

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
        # Find user by email
        stmt = select(User).where(
            func.lower(User.email) == func.lower(verify_data.email)
        )
        result = await db.execute(stmt)
        user = result.unique().scalar_one_or_none()

        if not user:
            return error_response(
                status_code=404,
                message="No account found with this email address",
            )

        # Find valid OTP for this user
        stmt = (
            select(UserOTP)
            .where(
                UserOTP.user_id == user.id,
                UserOTP.otp_code == verify_data.otp,
                UserOTP.is_used == False,
                UserOTP.is_verified == False,
            )
            .order_by(UserOTP.created_at.desc())
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
        # Extend expiration for reset token
        otp_record.expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )
        await db.commit()

        response = VerifyOTPResponse(
            email=user.email,
            reset_token=reset_token,
            message="OTP verified successfully. Use the reset token to set your new password.",
        )

        logger.info("OTP verified successfully for user: %s", user.email)

        return success_response(
            data=response.model_dump(),
            message="OTP verified successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("OTP verification error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Failed to verify OTP: {str(e)}")


async def reset_password(
    db: AsyncSession, reset_data: ResetPasswordRequest
) -> Optional[dict]:
    """
    Step 3: Reset user password using verified reset token.
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

        # Find user by email (case-insensitive)
        stmt = select(User).where(
            func.lower(User.email) == func.lower(reset_data.email)
        )
        result = await db.execute(stmt)
        user = result.unique().scalar_one_or_none()

        if not user:
            logger.warning(
                "User password reset attempt for non-existent email: %s",
                reset_data.email,
            )
            return error_response(
                status_code=404,
                message="User with this email not found",
            )

        if not user.active:
            return error_response(
                status_code=403,
                message="Account is inactive. Please contact administrator.",
            )

        # Find valid reset token
        stmt = (
            select(UserOTP)
            .where(
                UserOTP.user_id == user.id,
                UserOTP.reset_token == reset_data.reset_token,
                UserOTP.is_verified == True,
                UserOTP.is_used == False,
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
        user.password_hash = hash_password(reset_data.new_password)
        
        # Mark OTP as used (invalidate)
        otp_record.is_used = True
        
        await db.commit()
        await db.refresh(user)

        # Send success email (non-blocking)
        try:
            await send_password_reset_success_email(user.email, user.full_name)
        except Exception as email_error:
            logger.warning(
                "Failed to send password reset success email: %s", str(email_error)
            )

        logger.info("User password reset successful for: %s", user.email)

        # Clean up old OTPs for this user
        await db.execute(
            delete(UserOTP).where(
                UserOTP.user_id == user.id,
                UserOTP.is_used == True,
            )
        )
        await db.commit()

        return success_response(
            data={
                "email": user.email,
                "message": "Password has been reset successfully",
            },
            message="Password reset successful",
        )

    except Exception as e:  # pragma: no cover
        logger.error("User password reset error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"User password reset failed: {str(e)}")
