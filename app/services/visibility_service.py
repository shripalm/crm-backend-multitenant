from typing import Dict, List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.users import User
from app.models.roles import Role
from app.models.permissions import Permission
from app.utils.logging import logger


async def get_user_permissions(db: AsyncSession, user_id: str) -> Set[str]:
    """
    Extract all permission names for a given user via ORM relationships.

    Args:
        db: Database session
        user_id: UUID string of the user

    Returns:
        Set of permission names (e.g., {"contacts:read", "call_reports:create"})
    """
    try:
        # Query user with roles and permissions loaded
        stmt = select(User).where(User.id == user_id).options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            logger.warning(f"User not found: {user_id}")
            return set()

        # Extract all permission names from user's roles
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.name)

        logger.debug(f"User {user.email} has permissions: {permissions}")
        return permissions

    except Exception as e:
        logger.error(f"Error extracting permissions for user {user_id}: {str(e)}")
        return set()


async def aggregate_permissions_by_resource(permissions: Set[str]) -> Dict[str, List[str]]:
    """
    Aggregate permissions into a resource:action mapping.

    Args:
        permissions: Set of permission names (e.g., {"contacts:read", "contacts:create"})

    Returns:
        Dict mapping resource names to list of allowed actions
        (e.g., {"contacts": ["read", "create"], "call_reports": ["read"]})
    """
    resource_actions = {}

    for permission in permissions:
        try:
            # Split permission name into resource and action
            if ":" in permission:
                resource, action = permission.split(":", 1)
                if resource not in resource_actions:
                    resource_actions[resource] = []
                if action not in resource_actions[resource]:
                    resource_actions[resource].append(action)
            else:
                logger.warning(f"Invalid permission format: {permission}")

        except ValueError:
            logger.warning(f"Could not parse permission: {permission}")

    # Sort actions for consistent output
    for resource in resource_actions:
        resource_actions[resource].sort()

    return resource_actions


async def get_user_visibility_metadata(db: AsyncSession, user_id: str) -> Dict[str, List[str]]:
    """
    Get complete visibility metadata for a user.

    Args:
        db: Database session
        user_id: UUID string of the user

    Returns:
        Dict with resource:action mapping for UI/frontend consumption
    """
    permissions = await get_user_permissions(db, user_id)
    return await aggregate_permissions_by_resource(permissions)

