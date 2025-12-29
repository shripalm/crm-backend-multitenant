"""Agent Authentication Router with OTP-based password reset."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.admin_session import get_admin_db
from app.schemas.agent_auth_schema import (
    AgentLoginRequest,
    AgentLoginResponse,
    AgentRegisterRequest,
    AgentRegisterResponse,
    AgentResetPasswordRequest,
    AgentUpdateRequest,
    AgentResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
)
from app.schemas.response import StandardResponse
from app.services.agent_auth_service import (
    authenticate_agent,
    delete_agent,
    get_agent_by_id,
    get_agents_list,
    register_agent,
    request_password_reset_otp,
    reset_agent_password,
    update_agent,
    verify_password_reset_otp,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=StandardResponse[AgentRegisterResponse],
    summary="Register new agent",
    tags=["Agent Authentication"],
)
async def agent_register(
    register_data: AgentRegisterRequest,
    db: AsyncSession = Depends(get_admin_db),
):
    """Register a new agent with email, username, password, and profile details."""
    return await register_agent(db, register_data)


@router.post(
    "/login",
    response_model=StandardResponse[AgentLoginResponse],
    summary="Agent login",
    tags=["Agent Authentication"],
)
async def agent_login(
    login_data: AgentLoginRequest,
    db: AsyncSession = Depends(get_admin_db),
):
    """Authenticate agent using email/username and password. Returns JWT token."""
    return await authenticate_agent(db, login_data)


# ============== OTP-Based Password Reset Endpoints ==============


@router.post(
    "/forgot-password",
    response_model=StandardResponse[ForgotPasswordResponse],
    summary="Request password reset OTP",
    tags=["Agent Authentication"],
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
    
    **Flow:**
    1. POST /forgot-password (this endpoint) → Get OTP via email
    2. POST /verify-otp → Verify OTP and get reset token
    3. POST /reset-password → Reset password using reset token
    """
    return await request_password_reset_otp(db, request_data)


@router.post(
    "/verify-otp",
    response_model=StandardResponse[VerifyOTPResponse],
    summary="Verify password reset OTP",
    tags=["Agent Authentication"],
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
    
    **Note:** OTP expires after 10 minutes. Request a new one if expired.
    """
    return await verify_password_reset_otp(db, verify_data)


@router.post(
    "/reset-password",
    response_model=StandardResponse,
    summary="Reset agent password",
    tags=["Agent Authentication"],
)
async def agent_reset_password(
    reset_data: AgentResetPasswordRequest,
    db: AsyncSession = Depends(get_admin_db),
):
    """
    **Step 3: Reset password using verified reset token**
    
    - Provide email, reset_token (from verify-otp step), new_password, and confirm_password
    - Password must be at least 6 characters
    - new_password and confirm_password must match
    
    **Security:** Reset token is single-use and expires after 10 minutes.
    """
    return await reset_agent_password(db, reset_data)


# ============== Agent Management Endpoints ==============


@router.get(
    "/",
    response_model=StandardResponse[list[AgentResponse]],
    summary="Get all agents",
    
)
async def get_agents(
    db: AsyncSession = Depends(get_admin_db),
):
    """Get a list of all agents ordered by creation date (newest first)."""
    return await get_agents_list(db)


@router.get(
    "/{agent_id}",
    response_model=StandardResponse[AgentResponse],
    summary="Get agent by ID",
                      
)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_admin_db),
):
    """Get a specific agent by their UUID."""
    return await get_agent_by_id(db, agent_id)


@router.put(
    "/{agent_id}",
    response_model=StandardResponse[AgentResponse],
    summary="Update agent",
    
)
async def update_agent_endpoint(
    agent_id: str,
    update_data: AgentUpdateRequest,
    db: AsyncSession = Depends(get_admin_db),
):
    """
    Update agent information.
    
    - Only provided fields will be updated (partial update)
    - All registration fields can be updated including email and username
    - Email and username uniqueness will be validated
    - Returns the updated agent information
    
    **Note:** Password cannot be updated through this endpoint. Use password reset flow instead.
    """
    return await update_agent(db, agent_id, update_data)


@router.delete(
    "/{agent_id}",
    response_model=StandardResponse,
    summary="Delete agent",
    
)
async def delete_agent_endpoint(
    agent_id: str,
    db: AsyncSession = Depends(get_admin_db),
):
    """
    Delete an agent by their UUID.
    
    **Warning:** This action is irreversible and will permanently delete the agent.
    """
    return await delete_agent(db, agent_id)
