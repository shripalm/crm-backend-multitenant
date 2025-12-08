from typing import Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload

from app.models.roles import Role
from app.models.permissions import Permission
from app.models.mappings import role_permissions
from app.schemas.role_schema import RoleRead
from app.utils.logging import logger

from app.utils.response import success_response, error_response


async def create_role(db: AsyncSession, data: Any) -> Role:
    """Create a Role from `data` which must provide `.name` (and optionally `.description`).

    returns ValueError if required attributes are missing. Rolls back on DB error.
    """
    if not hasattr(data, "name"):
        return ValueError("`data` must have a `name` attribute")

    name = data.name
    description = getattr(data, "description", None)

    logger.debug("Role payload", name=name, description=description)
    role = Role(name=name, description=description)
    try:
        logger.info("Creating role", name=name)
        db.add(role)
        await db.commit()
        await db.refresh(role)
        role_data = RoleRead.model_validate(role).model_dump()
        logger.info("Role created", role_id=str(role.id))
        return success_response(role_data, message="Role created successfully")
    except Exception as e:
        logger.error(f"Failed to create role: {str(e)}")
        await db.rollback()
        return error_response(500, str(e))

async def list_roles(db: AsyncSession) -> List[Role]:
    """Return all Role instances."""
    try:
        roles = await db.execute(
            select(Role).options(selectinload(Role.permissions))
        )
        output = roles.scalars().all()
        output_data = [RoleRead.model_validate(r).model_dump() for r in output]
        logger.debug("Retrieved roles", count=len(output_data))
        return success_response(output_data, message="Roles retrieved successfully")
    except Exception as e:
        logger.error(f"Failed to list roles: {str(e)}")
        await db.rollback()
        return error_response(500, str(e))


async def assign_permission_to_role(db: AsyncSession, role_id: Any, permission_id: Any):
    """Attach a Permission to a Role by id. Returns the updated Role or None if not found.

    Performs a rollback on exception and avoids adding duplicate permissions.
    """
    try:
        role = await db.get(Role, role_id)
        perm = await db.get(Permission, permission_id)
        logger.debug(
            "Assign permission payload",
            role_id=str(role_id),
            permission_id=str(permission_id),
        )

        if role is None or perm is None:
            logger.warning("Role or permission not found for assignment", role_id=str(role_id), permission_id=str(permission_id))
            return error_response(404, "Role or Permission not found")

        # Avoid implicit lazy-loading of relationship collections (which can trigger
        # synchronous IO). Check the association table directly and insert if missing.
        stmt = select(role_permissions).where(
            role_permissions.c.role_id == role_id,
            role_permissions.c.permission_id == permission_id,
        )
        existing = await db.execute(stmt)
        if existing.first() is None:
            insert_stmt = insert(role_permissions).values(
                role_id=role_id, permission_id=permission_id
            )
            await db.execute(insert_stmt)
            await db.commit()

        # Fetch role with permissions loaded for serialization
        refreshed = await db.execute(
            select(Role).where(Role.id == role_id).options(selectinload(Role.permissions))
        )
        refreshed_role = refreshed.scalars().one_or_none()
        if refreshed_role is None:
            logger.warning("Role not found after permission assignment", role_id=str(role_id))
            return error_response(404, "Role not found after assignment")

        role_data = RoleRead.model_validate(refreshed_role).model_dump()
        logger.info("Permission assigned to role", role_id=str(role_id), permission_id=str(permission_id))
        return success_response(role_data, message="Permission assigned successfully")
    except Exception as e:
        logger.error(f"Failed to assign permission to role: {str(e)}")
        await db.rollback()
        return error_response(500, str(e))
