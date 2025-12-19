from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class AgentRegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Agent email")
    username: str = Field(..., min_length=3, max_length=255, description="Agent username")
    password: str = Field(..., min_length=6, max_length=100, description="Agent password")
    name: str = Field(..., max_length=255, description="Agent full name")
    contact_no: str = Field(..., max_length=50, description="Agent contact number")
    logo_url: Optional[str] = Field(None, max_length=512, description="Logo URL")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State")
    experience: Optional[str] = Field(None, max_length=100, description="Experience info")


class AgentRegisterResponse(BaseModel):
    agent_id: str = Field(..., description="Agent UUID")
    email: EmailStr
    username: str
    name: str


class AgentLoginRequest(BaseModel):
    email_or_username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=100)


class AgentLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    agent_id: str
    email: EmailStr
    username: str
    name: str
    expires_in: int


class AgentTokenPayload(BaseModel):
    agent_id: str
    email: EmailStr
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


# ============== Password Reset with OTP Schemas ==============


class ForgotPasswordRequest(BaseModel):
    """Request OTP for password reset - Step 1."""

    email: EmailStr = Field(..., description="Agent email address")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "agent@example.com"
            }
        }


class ForgotPasswordResponse(BaseModel):
    """Response after OTP is sent."""

    email: str = Field(..., description="Masked email address")
    message: str = Field(..., description="Success message")
    otp_expires_in_minutes: int = Field(..., description="OTP validity in minutes")


class VerifyOTPRequest(BaseModel):
    """Verify OTP - Step 2."""

    email: EmailStr = Field(..., description="Agent email address")
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
                "email": "agent@example.com",
                "otp": "1234"
            }
        }


class VerifyOTPResponse(BaseModel):
    """Response after successful OTP verification."""

    email: EmailStr = Field(..., description="Agent email address")
    reset_token: str = Field(..., description="Token to use for password reset")
    message: str = Field(..., description="Success message")


class AgentResetPasswordRequest(BaseModel):
    """Agent reset password request schema - Step 3 (requires verified OTP token)."""

    email: EmailStr = Field(..., description="Agent email address")
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
                "email": "agent@example.com",
                "reset_token": "abc123xyz...",
                "new_password": "NewPassword123",
                "confirm_password": "NewPassword123",
            }
        }
