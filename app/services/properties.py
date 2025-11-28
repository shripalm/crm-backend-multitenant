from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.projects import Property
from app.schemas.property_schema import PropertyCreate, PropertyRead
from app.utils.response import success_response, internal_server_error


async def create_property(db: AsyncSession, project_id: str, payload: PropertyCreate):
    try:
        data = payload.dict(exclude_none=True)
        new_property = Property(project_id=project_id, **data)

        db.add(new_property)
        await db.commit()
        await db.refresh(new_property)

        return success_response(
            data=PropertyRead.from_orm(new_property).dict(),
            message="Property created"
        )

    except Exception as e:
        await db.rollback()
        raise internal_server_error(f"Failed to create property: {str(e)}")


async def list_properties(db: AsyncSession, project_id: str):
    try:
        stmt = select(Property).where(
    Property.project_id == project_id,
    Property.is_deleted == False
)
        result = await db.execute(stmt)
        properties = result.scalars().all()

        data = [PropertyRead.from_orm(p).dict() for p in properties]

        return success_response(data=data, message="Properties fetched")

    except Exception as e:
        raise internal_server_error(f"Failed to list properties: {str(e)}")


async def soft_delete_property(db: AsyncSession, property_id: str):
    try:
        prop = await db.get(Property, property_id)
        if not prop:
            return None

        prop.is_deleted = True
        await db.commit()
        await db.refresh(prop)

        return success_response(message="Property soft deleted", data={})
    except Exception as e:
        await db.rollback()
        raise internal_server_error(str(e))


async def hard_delete_property(db: AsyncSession, property_id: str):
    try:
        prop = await db.get(Property, property_id)
        if not prop:
            return None

        await db.delete(prop)
        await db.commit()

        return success_response(message="Property permanently deleted", data={})
    except Exception as e:
        await db.rollback()
        raise internal_server_error(str(e))
