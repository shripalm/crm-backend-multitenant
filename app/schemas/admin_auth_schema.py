
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class AdminLoginRequest(BaseModel):
    """Admin login request schema - accepts email or username."""
    email_or_username: str = Field(
        ...,
        description="Admin email address or username",
        min_length=3,
        max_length=255,
        examples=["admin@example.com", "admin_user"],
    )
    password: str = Field(
        ...,
        description="Admin password",
        min_length=6,
        max_length=100,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email_or_username": "admin@example.com",
                "password": "yourpassword123",
            }
        }


class AdminLoginResponse(BaseModel):
    """Admin login response schema with JWT token."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    admin_id: int = Field(..., description="Admin ID")
    email: EmailStr = Field(..., description="Admin email")
    username: str = Field(..., description="Admin username")
    expires_in: int = Field(..., description="Token expiration time in minutes")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "admin_id": 1,
                "email": "admin@example.com",
                "username": "admin_user",
                "expires_in": 60,
            }
        }


class AdminTokenPayload(BaseModel):
    """JWT token payload schema for admin."""

    admin_id: int
    email: EmailStr
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


class AdminRegisterRequest(BaseModel):
    """Admin registration request schema."""

    email: EmailStr = Field(..., description="Admin email address")
    username: str = Field(
        ...,
        description="Admin username",
        min_length=3,
        max_length=50,
    )
    password: str = Field(
        ...,
        description="Admin password",
        min_length=6,
        max_length=100,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@example.com",
                "username": "admin_user",
                "password": "strongPassword123",
            }
        }


class AdminRegisterResponse(BaseModel):
    """Admin registration response schema."""

    admin_id: int = Field(..., description="Created admin ID")
    email: EmailStr = Field(..., description="Admin email")
    username: str = Field(..., description="Admin username")

    class Config:
        json_schema_extra = {
            "example": {
                "admin_id": 1,
                "email": "admin@example.com",
                "username": "admin_user",
            }
        }


class AdminResetPasswordRequest(BaseModel):
    """Admin reset password request schema - Step 3 (requires verified OTP token)."""

    email: EmailStr = Field(..., description="Admin email address")
    reset_token: str = Field(..., description="Reset token from OTP verification")
    new_password: str = Field(
        ...,
        description="New password",
        min_length=6,
        max_length=100,
    )
    confirm_password: str = Field(
        ...,
        description="Confirm new password",
        min_length=6,
        max_length=100,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@example.com",
                "reset_token": "abc123xyz...",
                "new_password": "NewPassword123",
                "confirm_password": "NewPassword123",
            }
        }


# ============== Password Reset with OTP Schemas ==============


class ForgotPasswordRequest(BaseModel):
    """Request OTP for password reset - Step 1."""

    email: EmailStr = Field(..., description="Admin email address")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@example.com"
            }
        }


class ForgotPasswordResponse(BaseModel):
    """Response after OTP is sent."""

    email: str = Field(..., description="Masked email address")
    message: str = Field(..., description="Success message")
    otp_expires_in_minutes: int = Field(..., description="OTP validity in minutes")


class VerifyOTPRequest(BaseModel):
    """Verify OTP - Step 2."""

    email: EmailStr = Field(..., description="Admin email address")
    otp: str = Field(
        ...,
        min_length=4,
        max_length=4,
        description="4-digit OTP code",
        pattern=r"^\d{4}$"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@example.com",
                "otp": "1234"
            }
        }


class VerifyOTPResponse(BaseModel):
    """Response after successful OTP verification."""

    email: EmailStr = Field(..., description="Admin email address")
    reset_token: str = Field(..., description="Token to use for password reset")
    message: str = Field(..., description="Success message")


# ============== Admin Management Schemas ==============


class AdminResponse(BaseModel):
    """Admin response schema for GET operations."""
    id: int = Field(..., description="Admin ID")
    email: EmailStr
    username: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminUpdateRequest(BaseModel):
    """Admin update request schema."""
    email: Optional[EmailStr] = Field(None, description="Admin email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Admin username")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "updated@example.com",
                "username": "updated_username"
            }
        }


