from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.roles import Role
from app.models.permissions import Permission


async def create_role(db: AsyncSession, data):
    role = Role(name=data.name, description=data.description)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def list_roles(db: AsyncSession):
    result = await db.execute(select(Role))
    return result.scalars().all()


async def assign_permission_to_role(db: AsyncSession, role_id, permission_id):
    role = await db.get(Role, role_id)
    perm = await db.get(Permission, permission_id)

    if not role or not perm:
        return None

    role.permissions.append(perm)
    await db.commit()
    await db.refresh(role)
    return role
