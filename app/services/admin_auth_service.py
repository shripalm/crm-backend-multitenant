from datetime import timedelta
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, verify_password, hash_password
from app.models.admin import Admin
from app.schemas.admin_auth_schema import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminRegisterRequest,
    AdminRegisterResponse,
    AdminResetPasswordRequest,
)
from app.utils.logging import logger
from app.utils.response import error_response, internal_server_error, success_response


async def authenticate_admin(
    db: AsyncSession, login_data: AdminLoginRequest
) -> Optional[dict]:
    """Authenticate admin with email/username and password and return JWT token."""

    try:
        email_or_username = login_data.email_or_username.strip()

        stmt = select(Admin).where(
            or_(
                func.lower(Admin.email) == func.lower(email_or_username),
                func.lower(Admin.username) == func.lower(email_or_username),
            )
        )

        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            logger.warning(
                "Admin login failed - admin not found: %s", email_or_username
            )
            return error_response(
                status_code=401,
                message="Invalid email/username or password",
            )

        if not verify_password(login_data.password, admin.password_hash):
            logger.warning(
                "Admin login failed - invalid password for admin: %s", admin.email
            )
            return error_response(
                status_code=401,
                message="Invalid email/username or password",
            )

        token_data = {
            "admin_id": admin.id,
            "email": admin.email,
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        login_response = AdminLoginResponse(
            access_token=access_token,
            token_type="bearer",
            admin_id=admin.id,
            email=admin.email,
            username=admin.username,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        logger.info("Admin logged in successfully: %s", admin.email)

        return success_response(
            data=login_response.model_dump(),
            message="Login successful",
        )

    except Exception as e:  # pragma: no cover - defensive
        logger.error("Admin login error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Authentication failed: {str(e)}")


async def register_admin(
    db: AsyncSession, register_data: AdminRegisterRequest
) -> Optional[dict]:
    """Register a new admin user.

    Ensures email and username are unique and stores a hashed password.
    """

    try:
        # Check if email or username already exists
        stmt = select(Admin).where(
            or_(
                func.lower(Admin.email) == func.lower(register_data.email),
                func.lower(Admin.username) == func.lower(register_data.username),
            )
        )

        result = await db.execute(stmt)
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            logger.warning(
                "Admin registration failed - email or username already exists: %s / %s",
                register_data.email,
                register_data.username,
            )
            return error_response(
                status_code=400,
                message="Admin with this email or username already exists",
            )

        # Create new admin with hashed password
        admin = Admin(
            email=register_data.email,
            username=register_data.username,
            password_hash=hash_password(register_data.password),
        )

        db.add(admin)
        await db.commit()
        await db.refresh(admin)

        response = AdminRegisterResponse(
            admin_id=admin.id,
            email=admin.email,
            username=admin.username,
        )

        logger.info("Admin registered successfully: %s", admin.email)

        return success_response(
            data=response.model_dump(),
            message="Admin registered successfully",
        )

    except Exception as e:  # pragma: no cover - defensive
        logger.error("Admin registration error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Admin registration failed: {str(e)}")


async def reset_admin_password(
    db: AsyncSession, reset_data: AdminResetPasswordRequest
) -> Optional[dict]:
    """Reset admin password using email, new_password and confirm_password."""

    try:
        # Validate passwords match
        if reset_data.new_password != reset_data.confirm_password:
            return error_response(
                status_code=400,
                message="Passwords do not match",
            )

        # Find admin by email (case-insensitive)
        stmt = select(Admin).where(
            func.lower(Admin.email) == func.lower(reset_data.email)
        )
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            logger.warning(
                "Admin password reset attempt for non-existent email: %s",
                reset_data.email,
            )
            return error_response(
                status_code=404,
                message="Admin with this email not found",
            )

        # Update password
        admin.password_hash = hash_password(reset_data.new_password)
        await db.commit()
        await db.refresh(admin)

        logger.info("Admin password reset successful for: %s", admin.email)

        return success_response(
            data={
                "email": admin.email,
                "message": "Password has been reset successfully",
            },
            message="Password reset successful",
        )

    except Exception as e:  # pragma: no cover - defensive
        logger.error("Admin password reset error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Admin password reset failed: {str(e)}")
