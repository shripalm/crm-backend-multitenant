"""User Authentication Router with OTP-based password reset."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.db.session import get_db
from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
    VerifyOTPRequest,
    VerifyOTPResponse,
)
from app.schemas.response import StandardResponse
from app.services.auth_service import (
    authenticate_user,
    request_password_reset_otp,
    reset_password,
    verify_password_reset_otp,
    verify_user_token,
)
from app.utils.logging import logger

router = APIRouter()
# security = HTTPBearer()


@router.post("/login", response_model=StandardResponse[LoginResponse])
async def login(
    login_data: LoginRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    User login endpoint.
    
    Accepts either email or username along with password.
    Returns JWT access token on successful authentication.
    
    - **email_or_username**: User's email address or username
    - **password**: User's password (minimum 6 characters)
    """
    return await authenticate_user(db, login_data)


# ============== OTP-Based Password Reset Endpoints ==============


@router.post(
    "/forgot-password",
    response_model=StandardResponse[ForgotPasswordResponse],
)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
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
)
async def verify_otp(
    verify_data: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db)
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
)
async def user_reset_password(
    reset_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    **Step 3: Reset password using verified reset token**
    
    - Provide email, reset_token (from verify-otp step), new_password, and confirm_password
    - Password must be at least 6 characters
    """
    return await reset_password(db, reset_data)
