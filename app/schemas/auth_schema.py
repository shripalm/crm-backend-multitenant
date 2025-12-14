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


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema."""
    email: EmailStr = Field(
        ..., 
        description="User's email address"
    )
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
                "new_password": "newpassword123",
                "confirm_password": "newpassword123"
            }
        }
