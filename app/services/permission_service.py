from typing import Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.permissions import Permission
from app.schemas.permission_schema import PermissionRead
from app.utils.response import success_response, internal_server_error


async def create_permission(db: AsyncSession, data: Any):
    """Create a Permission and return a serialized response."""
    try:
        perm = Permission(
            name=data.name,
            label=data.label,
            description=data.description,
        )
        db.add(perm)
        await db.commit()
        await db.refresh(perm)

        perm_data = PermissionRead.model_validate(perm).model_dump()
        return success_response(data=perm_data, message="Permission created")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to create permission: {str(e)}")


async def list_permissions(db: AsyncSession) -> List[dict]:
    """Return all permissions as serialized dicts."""
    try:
        result = await db.execute(select(Permission))
        perms = result.scalars().all()
        data = [PermissionRead.model_validate(p).model_dump() for p in perms]
        return success_response(data=data, message="Permissions retrieved")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to list permissions: {str(e)}")
