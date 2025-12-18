from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.projects import Property
from app.schemas.property_schema import PropertyCreate, PropertyRead
from app.utils.response import success_response, internal_server_error, error_response
from app.utils.logging import logger


async def create_property(db: AsyncSession, project_id: str, payload: PropertyCreate):
    try:
        data = payload.dict(exclude_none=True)
        logger.info("Creating property", project_id=project_id)
        logger.debug("Property payload", project_id=project_id, payload=data)
        new_property = Property(project_id=project_id, **data)

        db.add(new_property)
        await db.commit()
        await db.refresh(new_property)

        logger.info("Property created", property_id=str(new_property.id))
        return success_response(
            data=PropertyRead.from_orm(new_property).dict(),
            message="Property created"
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create property: {str(e)}")
        return internal_server_error(f"Failed to create property: {str(e)}")


async def list_properties(db: AsyncSession, project_id: str):
    try:
        stmt = select(Property).where(
    Property.project_id == project_id,
    Property.is_deleted == False
)
        result = await db.execute(stmt)
        properties = result.scalars().all()

        data = [PropertyRead.from_orm(p).dict() for p in properties]

        logger.debug("Listed properties", project_id=project_id, count=len(data))
        return success_response(data=data, message="Properties fetched")

    except Exception as e:
        logger.error(f"Failed to list properties: {str(e)}")
        return internal_server_error(f"Failed to list properties: {str(e)}")


async def soft_delete_property(db: AsyncSession, property_id: str):
    try:
        prop = await db.get(Property, property_id)
        if not prop:
            logger.warning("Property not found for soft delete", property_id=property_id)
            return error_response(404, "Property not found")

        prop.is_deleted = True
        await db.commit()
        await db.refresh(prop)

        logger.info("Property soft deleted", property_id=property_id)
        logger.debug("Property soft delete state", property_id=property_id, is_deleted=prop.is_deleted)
        return success_response(message="Property soft deleted", data={})
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to soft delete property: {str(e)}")
        return internal_server_error(str(e))
