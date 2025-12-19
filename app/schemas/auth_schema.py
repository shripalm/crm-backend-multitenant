from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request schema - accepts email or username."""
    email_or_username: str = Field(
        ..., 
        description="Email address or username",
        min_length=3,
        max_length=255,
        examples=["user@example.com", "john_doe"]
    )
    password: str = Field(
        ..., 
        description="User password",
        min_length=6,
        max_length=100
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email_or_username": "user@example.com",
                "password": "yourpassword123"
            }
        }


class LoginResponse(BaseModel):
    """Login response schema with user info and JWT token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    expires_in: int = Field(..., description="Token expiration time in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "expires_in": 60
            }
        }


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    user_id: str
    email: str
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


class ResetPasswordRequest(BaseModel):
    """Reset password request schema - Step 3 (requires verified OTP token)."""
    email: EmailStr = Field(..., description="User's email address")
    reset_token: str = Field(..., description="Reset token from OTP verification")
    new_password: str = Field(
        ..., 
        description="New password",
        min_length=6,
        max_length=100
    )
    confirm_password: str = Field(
        ..., 
        description="Confirm new password",
        min_length=6,
        max_length=100
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "reset_token": "abc123xyz...",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123"
            }
        }


# ============== Password Reset with OTP Schemas ==============


class ForgotPasswordRequest(BaseModel):
    """Request OTP for password reset - Step 1."""

    email: EmailStr = Field(..., description="User email address")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class ForgotPasswordResponse(BaseModel):
    """Response after OTP is sent."""

    email: str = Field(..., description="Masked email address")
    message: str = Field(..., description="Success message")
    otp_expires_in_minutes: int = Field(..., description="OTP validity in minutes")


class VerifyOTPRequest(BaseModel):
    """Verify OTP - Step 2."""

    email: EmailStr = Field(..., description="User email address")
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
                "email": "user@example.com",
                "otp": "1234"
            }
        }


class VerifyOTPResponse(BaseModel):
    """Response after successful OTP verification."""

    email: EmailStr = Field(..., description="User email address")
    reset_token: str = Field(..., description="Token to use for password reset")
    message: str = Field(..., description="Success message")

