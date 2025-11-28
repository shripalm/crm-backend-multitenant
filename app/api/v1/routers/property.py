from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.property_schema import PropertyCreate
from app.schemas.response import StandardResponse
from app.services.properties import create_property, list_properties ,soft_delete_property,hard_delete_property

router = APIRouter()


@router.post(
    "/{project_id}/properties",
    response_model=StandardResponse[dict]
)
async def add_property(
    project_id: str,
    payload: PropertyCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a property to a given project"""
    return await create_property(db, project_id, payload)


@router.get(
    "/{project_id}/properties",
    response_model=StandardResponse[List[dict]]
)
async def get_properties(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """List all properties of a project"""
    return await list_properties(db, project_id)



@router.delete("/property/{property_id}/soft")
async def delete_property_soft(property_id: str, db: AsyncSession = Depends(get_db)):
    return await soft_delete_property(db, property_id)


@router.delete("/property/{property_id}/hard")
async def delete_property_hard(property_id: str, db: AsyncSession = Depends(get_db)):
    return await hard_delete_property(db, property_id)
