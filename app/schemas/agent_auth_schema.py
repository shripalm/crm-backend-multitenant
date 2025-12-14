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


class AgentResetPasswordRequest(BaseModel):
    """Agent reset password request schema."""

    email: EmailStr = Field(..., description="Agent email address")
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
                "new_password": "NewPassword123",
                "confirm_password": "NewPassword123",
            }
        }
