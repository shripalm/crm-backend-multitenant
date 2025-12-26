"""Admin Authentication Service with OTP-based password reset."""
import random
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.admin import Admin
from app.models.admin_otp import AdminOTP
from app.schemas.admin_auth_schema import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminRegisterRequest,
    AdminRegisterResponse,
    AdminResetPasswordRequest,
    AdminUpdateRequest,
    AdminResponse,
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
        # Find admin by email (case-insensitive)
        stmt = select(Admin).where(
            func.lower(Admin.email) == func.lower(request_data.email)
        )
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            logger.warning(
                "Password reset OTP requested for non-existent email: %s",
                request_data.email,
            )
            return error_response(
                status_code=404,
                message="No account found with this email address",
            )

        # Invalidate any existing OTPs for this admin
        await db.execute(
            update(AdminOTP)
            .where(AdminOTP.admin_id == admin.id, AdminOTP.is_used == False)
            .values(is_used=True)
        )

        # Generate new OTP
        otp_code = generate_otp(settings.OTP_LENGTH)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )

        # Store OTP in database
        otp_record = AdminOTP(
            admin_id=admin.id,
            email=admin.email,
            otp_code=otp_code,
            expires_at=expires_at,
            is_verified=False,
            is_used=False,
        )
        db.add(otp_record)
        await db.commit()

        # Send OTP via email (assuming 'admin' has a name or using 'Admin User')
        admin_name = getattr(admin, "username", "Admin User")
        
        email_sent = await send_otp_email(
            to_email=admin.email,
            otp_code=otp_code,
            agent_name=admin_name, # Reusing param name, acts as recipient name
        )

        if not email_sent:
            logger.error("Failed to send OTP email to: %s", admin.email)
            return error_response(
                status_code=500,
                message="Failed to send OTP email. Please try again later.",
            )

        response = ForgotPasswordResponse(
            email=mask_email(admin.email),
            message="OTP has been sent to your registered email address",
            otp_expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
        )

        logger.info("Password reset OTP sent to admin: %s", admin.email)

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
        # Find admin by email
        stmt = select(Admin).where(
            func.lower(Admin.email) == func.lower(verify_data.email)
        )
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            return error_response(
                status_code=404,
                message="No account found with this email address",
            )

        # Find valid OTP for this admin
        stmt = (
            select(AdminOTP)
            .where(
                AdminOTP.admin_id == admin.id,
                AdminOTP.otp_code == verify_data.otp,
                AdminOTP.is_used == False,
                AdminOTP.is_verified == False,
            )
            .order_by(AdminOTP.created_at.desc())
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
            email=admin.email,
            reset_token=reset_token,
            message="OTP verified successfully. Use the reset token to set your new password.",
        )

        logger.info("OTP verified successfully for admin: %s", admin.email)

        return success_response(
            data=response.model_dump(),
            message="OTP verified successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("OTP verification error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Failed to verify OTP: {str(e)}")


async def reset_admin_password(
    db: AsyncSession, reset_data: AdminResetPasswordRequest
) -> Optional[dict]:
    """
    Step 3: Reset admin password using verified reset token.
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

        # Find valid reset token
        stmt = (
            select(AdminOTP)
            .where(
                AdminOTP.admin_id == admin.id,
                AdminOTP.reset_token == reset_data.reset_token,
                AdminOTP.is_verified == True,
                AdminOTP.is_used == False,
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
        admin.password_hash = hash_password(reset_data.new_password)
        
        # Mark OTP as used (invalidate)
        otp_record.is_used = True
        
        await db.commit()
        await db.refresh(admin)

        # Send success email (non-blocking)
        admin_name = getattr(admin, "username", "Admin User")
        try:
            await send_password_reset_success_email(admin.email, admin_name)
        except Exception as email_error:
            logger.warning(
                "Failed to send password reset success email: %s", str(email_error)
            )

        logger.info("Admin password reset successful for: %s", admin.email)

        # Clean up old OTPs for this admin
        await db.execute(
            delete(AdminOTP).where(
                AdminOTP.admin_id == admin.id,
                AdminOTP.is_used == True,
            )
        )
        await db.commit()

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


# ============== Admin Management Functions ==============


async def get_admins_list(db: AsyncSession) -> Optional[dict]:
    """Get list of all admins."""
    try:
        stmt = select(Admin).order_by(Admin.created_at.desc())
        result = await db.execute(stmt)
        admins = result.scalars().all()

        admin_responses = []
        for admin in admins:
            admin_response = AdminResponse(
                id=admin.id,
                email=admin.email,
                username=admin.username,
                created_at=admin.created_at,
                updated_at=admin.updated_at,
            )
            admin_responses.append(admin_response)

        return success_response(
            data=admin_responses,
            message="Admins retrieved successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Get admins list error: %s", str(e), exc_info=True)
        return internal_server_error(f"Failed to retrieve admins: {str(e)}")


async def get_admin_by_id(db: AsyncSession, admin_id: int) -> Optional[dict]:
    """Get a specific admin by ID."""
    try:
        stmt = select(Admin).where(Admin.id == admin_id)
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            return error_response(
                status_code=404,
                message="Admin not found",
            )

        admin_response = AdminResponse(
            id=admin.id,
            email=admin.email,
            username=admin.username,
            created_at=admin.created_at,
            updated_at=admin.updated_at,
        )

        return success_response(
            data=admin_response.model_dump(),
            message="Admin retrieved successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Get admin by ID error: %s", str(e), exc_info=True)
        return internal_server_error(f"Failed to retrieve admin: {str(e)}")


async def update_admin(
    db: AsyncSession, admin_id: int, update_data: AdminUpdateRequest
) -> Optional[dict]:
    """Update admin information."""
    try:
        # Check if admin exists
        stmt = select(Admin).where(Admin.id == admin_id)
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            return error_response(
                status_code=404,
                message="Admin not found",
            )

        # Check for email and username uniqueness if they are being updated
        if update_data.email is not None or update_data.username is not None:
            conditions = []
            if update_data.email is not None:
                conditions.append(func.lower(Admin.email) == func.lower(update_data.email))
            if update_data.username is not None:
                conditions.append(func.lower(Admin.username) == func.lower(update_data.username))
            
            if conditions:
                stmt = select(Admin).where(
                    or_(*conditions),
                    Admin.id != admin_id  # Exclude current admin from check
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

        if not update_values:
            return error_response(
                status_code=400,
                message="No fields to update",
            )

        # Apply updates
        stmt = (
            update(Admin)
            .where(Admin.id == admin_id)
            .values(**update_values)
            .returning(Admin)
        )
        result = await db.execute(stmt)
        await db.commit()
        updated_admin = result.scalar_one()

        admin_response = AdminResponse(
            id=updated_admin.id,
            email=updated_admin.email,
            username=updated_admin.username,
            created_at=updated_admin.created_at,
            updated_at=updated_admin.updated_at,
        )

        logger.info("Admin updated successfully: %s", admin_id)

        return success_response(
            data=admin_response.model_dump(),
            message="Admin updated successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Update admin error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Failed to update admin: {str(e)}")


async def delete_admin(db: AsyncSession, admin_id: int) -> Optional[dict]:
    """Delete an admin by ID."""
    try:
        # Check if admin exists
        stmt = select(Admin).where(Admin.id == admin_id)
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            return error_response(
                status_code=404,
                message="Admin not found",
            )

        # Delete admin
        stmt = delete(Admin).where(Admin.id == admin_id)
        await db.execute(stmt)
        await db.commit()

        logger.info("Admin deleted successfully: %s", admin_id)

        return success_response(
            data={"admin_id": admin_id},
            message="Admin deleted successfully",
        )

    except Exception as e:  # pragma: no cover
        logger.error("Delete admin error: %s", str(e), exc_info=True)
        await db.rollback()
        return internal_server_error(f"Failed to delete admin: {str(e)}")
