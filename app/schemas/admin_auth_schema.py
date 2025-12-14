
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
    """Admin reset password request schema."""

    email: EmailStr = Field(..., description="Admin email address")
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
                "new_password": "NewPassword123",
                "confirm_password": "NewPassword123",
            }
        }

