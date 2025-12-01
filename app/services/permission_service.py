from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.permissions import Permission


async def create_permission(db: AsyncSession, data):
    perm = Permission(
        name=data.name,
        label=data.label,
        description=data.description
    )
    db.add(perm)
    await db.commit()
    await db.refresh(perm)
    return perm


async def list_permissions(db: AsyncSession):
    result = await db.execute(select(Permission))
    return result.scalars().all()
