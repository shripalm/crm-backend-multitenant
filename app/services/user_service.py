from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User
from app.models.roles import Role

from app.core.security import hash_password


async def create_user(db: AsyncSession, data):
    """Create new user"""

    user = User(
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def list_users(db: AsyncSession):
    """List all users"""
    result = await db.execute(select(User))
    return result.scalars().all()


async def assign_role_to_user(db: AsyncSession, user_id, role_id):
    """Assign a role to a user"""
    user = await db.get(User, user_id)
    role = await db.get(Role, role_id)

    if not user or not role:
        return None

    user.roles.append(role)
    await db.commit()
    await db.refresh(user)

    return user
