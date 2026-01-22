from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Any

from app.db.session import get_db
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate
from app.schemas.response import StandardResponse
from app.services.user_service import (
    create_user,
    list_users,
    assign_role_to_user,
    update_user,
    delete_user
)

router = APIRouter()


@router.post("/", response_model=StandardResponse[UserRead])
async def add_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, payload)


@router.get("/", response_model=StandardResponse[list[UserRead]])
async def get_users(db: AsyncSession = Depends(get_db)):
    return await list_users(db)


@router.get("/{user_id}", response_model=StandardResponse[UserRead])
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    # Reuse list_users but filter by ID
    result = await list_users(db)
    if result.status != 200:
        return result
        
    user = next((u for u in result.data if u["id"] == str(user_id)), None)
    if not user:
        from app.utils.response import error_response
        return error_response(404, "User not found")
        
    result.data = user
    return result


@router.patch("/{user_id}", response_model=StandardResponse[UserRead])
async def update_user_endpoint(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user details."""
    return await update_user(db, user_id, payload)


@router.delete("/{user_id}", response_model=StandardResponse[dict[str, str]])
async def delete_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a user by ID."""
    return await delete_user(db, user_id)


@router.post("/{user_id}/roles/{role_id}", response_model=StandardResponse)
async def add_role_to_user(user_id: UUID, role_id: UUID, db: AsyncSession = Depends(get_db)):
    return await assign_role_to_user(db, user_id, role_id)