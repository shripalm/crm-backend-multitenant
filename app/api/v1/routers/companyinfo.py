from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.admin_session import get_admin_db
from app.schemas.companyinfo_schema import CompanyInfoRead, CompanyInfoCreate, CompanyInfoUpdate
from uuid import UUID   
from app.services.companyinfo_service import (
    create_company_info,  
    list_company_info,      
    get_company_info,
    update_company_info,
)
from app.schemas.response import StandardResponse

router = APIRouter()

@router.post("/", response_model=StandardResponse[CompanyInfoRead])
async def add_company_info(payload: CompanyInfoCreate, db: AsyncSession = Depends(get_admin_db)):
    """Create a new company info"""
    return await create_company_info(db, payload)


@router.get("/", response_model=StandardResponse[list[CompanyInfoRead]])
async def get_company_info_list(db: AsyncSession = Depends(get_admin_db)):
    """Retrieve a list of all company info"""
    return await list_company_info(db)


@router.get("/{company_info_id}", response_model=StandardResponse)
async def get_company_info_by_id(company_info_id: UUID, db: AsyncSession = Depends(get_admin_db)):
    """Get a single company info by ID"""
    return await get_company_info(db, company_info_id)

@router.put("/{company_info_id}", response_model=StandardResponse)
async def update_company_info_by_id(
    company_info_id: UUID, payload: CompanyInfoUpdate, db: AsyncSession = Depends(get_admin_db)
):
    """Update an existing company info"""
    return await update_company_info(db, company_info_id, payload)  