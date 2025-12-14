from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.admin_session import get_admin_db
from app.schemas.admin_auth_schema import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminRegisterRequest,
    AdminRegisterResponse,
    AdminResetPasswordRequest,
)
from app.schemas.response import StandardResponse
from app.services.admin_auth_service import (
    authenticate_admin,
    register_admin,
    reset_admin_password,
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
    """Reset admin password using email, new_password, and confirm_password."""
    return await reset_admin_password(db, reset_data)
