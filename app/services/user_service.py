from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.models.users import User
from app.models.roles import Role
from app.models.mappings import user_roles
from app.utils.logging import logger

from app.core.security import hash_password
from app.schemas.user_schema import UserRead
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)


async def create_user(db: AsyncSession, data: Any):
    """Create new user and return serialized response."""
    try:
        logger.info(f"Creating user: {data}")
        user = User(
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            team_name=getattr(data, "team_name", None),
            agent_id=getattr(data, "agent_id", None),
            contact=getattr(data, "contact", None),
            gender=getattr(data, "gender", None),
            address=getattr(data, "address", None),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        user_data = UserRead.model_validate(user).model_dump()
        logger.info(f"User created successfully: {user_data}")
        return success_response(data=user_data, message="User created")

    except IntegrityError as e:
        await db.rollback()
        # Check if it's a duplicate email error
        if "users_email_key" in str(e) or "duplicate key value violates unique constraint" in str(e):
            logger.warning(f"Duplicate email attempt: {data.email}")
            return error_response(409, "User with this email already exists")
        else:
            logger.error(f"Integrity error creating user: {str(e)}")
            return internal_server_error(f"Failed to create user: {str(e)}")
    
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to create user: {str(e)}")


async def list_users(db: AsyncSession):
    """List all users and return serialized response."""
    try:
        # Eagerly load User.roles and Role.permissions to prevent MissingGreenlet errors
        stmt = select(User).options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        result = await db.execute(stmt)
        users = result.scalars().all()
        logger.debug(f"api/v1/users/list_users: Retrieved users: {users}")

        if not users:
            return error_response(404, "No users found")

        data = [UserRead.model_validate(u).model_dump() for u in users]
        return success_response(data=data, message="Users retrieved")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to list users: {str(e)}")


async def assign_role_to_user(db: AsyncSession, user_id: Any, role_id: Any):
    """Assign a role to a user safely (uses association table to avoid lazy loads)."""
    try:
        user = await db.get(User, user_id)
        role = await db.get(Role, role_id)

        if user is None or role is None:
            return error_response(404, "User or Role not found")

        # Check association table to avoid relationship lazy-loading
        stmt = select(user_roles).where(
            user_roles.c.user_id == user_id,
            user_roles.c.role_id == role_id,
        )
        existing = await db.execute(stmt)
        if existing.first() is None:
            insert_stmt = insert(user_roles).values(user_id=user_id, role_id=role_id)
            await db.execute(insert_stmt)
            await db.commit()

        # Refresh user with roles and permissions eagerly loaded for serialization
        refreshed = await db.execute(
            select(User).where(User.id == user_id).options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
        )
        refreshed_user = refreshed.scalars().one_or_none()
        if refreshed_user is None:
            return error_response(404, "User not found after assignment")

        user_data = UserRead.model_validate(refreshed_user).model_dump()
        return success_response(data=user_data, message="Role assigned to user")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to assign role: {str(e)}")
