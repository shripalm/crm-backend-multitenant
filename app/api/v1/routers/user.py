from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.schemas.user_schema import UserCreate, UserRead
from app.services.user_service import (
    create_user,
    list_users,
    assign_role_to_user
)

router = APIRouter()


@router.post("/", response_model=UserRead)
async def add_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, payload)


@router.get("/", response_model=list[UserRead])
async def get_users(db: AsyncSession = Depends(get_db)):
    return await list_users(db)


@router.post("/{user_id}/roles/{role_id}")
async def add_role_to_user(user_id: UUID, role_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await assign_role_to_user(db, user_id, role_id)
    if not user:
        raise HTTPException(status_code=404, detail="User or Role not found")
    return {"message": "Role assigned successfully", "user": user}
