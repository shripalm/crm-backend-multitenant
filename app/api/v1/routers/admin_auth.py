"""Admin Authentication Router with OTP-based password reset."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.admin_session import get_admin_db
from app.schemas.admin_auth_schema import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminRegisterRequest,
    AdminRegisterResponse,
    AdminResetPasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
)
from app.schemas.response import StandardResponse
from app.services.admin_auth_service import (
    authenticate_admin,
    register_admin,
    request_password_reset_otp,
    reset_admin_password,
    verify_password_reset_otp,
)

router = APIRouter()


@router.post(
    "/login",
    response_model=StandardResponse[AdminLoginResponse],
    summary="Admin login",
    tags=["Admin Authentication"],
)
async def admin_login(
    login_data: AdminLoginRequest,
    db: AsyncSession = Depends(get_admin_db),
):
    """Admin login endpoint using email/username and password."""
    return await authenticate_admin(db, login_data)


@router.post(
    "/register",
    response_model=StandardResponse[AdminRegisterResponse],
    summary="Register new admin",
    tags=["Admin Authentication"],
)
async def admin_register(
    register_data: AdminRegisterRequest,
    db: AsyncSession = Depends(get_admin_db),
):
    """Register a new admin with email, username, and password."""
    return await register_admin(db, register_data)


# ============== OTP-Based Password Reset Endpoints ==============


@router.post(
    "/forgot-password",
    response_model=StandardResponse[ForgotPasswordResponse],
    summary="Request password reset OTP",
    tags=["Admin Authentication"],
)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_admin_db),
):
    """
    **Step 1: Request OTP for password reset**
    
    - Provide the registered email address
    - If the email exists, a 4-digit OTP will be sent to that email
    - OTP is valid for 10 minutes
    """
    return await request_password_reset_otp(db, request_data)


@router.post(
    "/verify-otp",
    response_model=StandardResponse[VerifyOTPResponse],
    summary="Verify password reset OTP",
    tags=["Admin Authentication"],
)
async def verify_otp(
    verify_data: VerifyOTPRequest,
    db: AsyncSession = Depends(get_admin_db),
):
    """
    **Step 2: Verify the OTP received via email**
    
    - Provide the email and 4-digit OTP received
    - On success, you'll receive a reset token
    - Use the reset token in the next step to set your new password
    """
    return await verify_password_reset_otp(db, verify_data)


@router.post(
    "/reset-password",
    response_model=StandardResponse,
    summary="Reset admin password",
    tags=["Admin Authentication"],
)
async def admin_reset_password(
    reset_data: AdminResetPasswordRequest,
    db: AsyncSession = Depends(get_admin_db),
):
    """
    **Step 3: Reset password using verified reset token**
    
    - Provide email, reset_token (from verify-otp step), new_password, and confirm_password
    - Password must be at least 6 characters
    """
    return await reset_admin_password(db, reset_data)
