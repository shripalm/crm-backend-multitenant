from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.agent_auth_schema import (
    AgentLoginRequest,
    AgentLoginResponse,
    AgentRegisterRequest,
    AgentRegisterResponse,
    AgentResetPasswordRequest,
)
from app.schemas.response import StandardResponse
from app.services.agent_auth_service import (
    authenticate_agent,
    register_agent,
    reset_agent_password,
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
    db: AsyncSession = Depends(get_db),
):
    return await register_agent(db, register_data)


@router.post(
    "/login",
    response_model=StandardResponse[AgentLoginResponse],
    summary="Agent login",
    tags=["Agent Authentication"],
)
async def agent_login(
    login_data: AgentLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await authenticate_agent(db, login_data)


@router.post(
    "/reset-password",
    response_model=StandardResponse,
    summary="Reset agent password",
    tags=["Agent Authentication"],
)
async def agent_reset_password(
    reset_data: AgentResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset agent password using email, new_password, and confirm_password."""
    return await reset_agent_password(db, reset_data)
