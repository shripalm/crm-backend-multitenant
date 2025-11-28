from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.schemas.role_schema import RoleCreate, RoleRead
from app.services.role_service import (
    create_role,
    list_roles,
    assign_permission_to_role
)

router = APIRouter()


@router.post("/", response_model=RoleRead)
async def add_role(payload: RoleCreate, db: AsyncSession = Depends(get_db)):
    return await create_role(db, payload)


@router.get("/", response_model=list[RoleRead])
async def get_roles(db: AsyncSession = Depends(get_db)):
    return await list_roles(db)


@router.post("/{role_id}/permissions/{permission_id}")
async def add_permission(role_id: UUID, permission_id: UUID, db: AsyncSession = Depends(get_db)):
    role = await assign_permission_to_role(db, role_id, permission_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role or Permission not found")
    return {"message": "Permission assigned successfully", "role": role}
