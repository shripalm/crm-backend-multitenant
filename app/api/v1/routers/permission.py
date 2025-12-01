from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.response import StandardResponse

from app.db.session import get_db
from app.schemas.permission_schema import PermissionCreate, PermissionRead
from app.services.permission_service import (
    create_permission,
    list_permissions
)

router = APIRouter()


@router.post("/", response_model=StandardResponse[PermissionRead])
async def add_permission(payload: PermissionCreate, db: AsyncSession = Depends(get_db)):
    return await create_permission(db, payload)


@router.get("/", response_model=StandardResponse[list[PermissionRead]])
async def get_permissions(db: AsyncSession = Depends(get_db)):
    return await list_permissions(db)
