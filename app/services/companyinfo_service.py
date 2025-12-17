from http.client import HTTPException
from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.utils.logging import logger
from app.models.companyinfo import CompanyInfo
from app.schemas.companyinfo_schema import CompanyInfoCreate, CompanyInfoRead, CompanyInfoUpdate
from app.utils.response import (   
    success_response,
    error_response,
    internal_server_error,
)


async def create_company_info(db: AsyncSession, data: CompanyInfoCreate):
    try:
        logger.info("Creating Company Info",company_size=str(data.company_size) , name=data.name)
        company_info = CompanyInfo(
            name = data.name,
            address = data.address,
            phone_number = data.phone_number,
            email = data.email,
            company_size = data.company_size,
            description = data.description,
        )

        db.add(company_info)
        await db.commit()
        await db.refresh(company_info)

        company_info_data = CompanyInfoRead.model_validate(company_info).model_dump()
        logger.info("Company Info created successfully", company_id = str(company_info.company_id))
        return success_response(data=company_info_data, message="Company Info created successfully")
    
    except Exception as e:
        logger.error(f"Failed to create company info:{str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to create company info:{str(e)}")

async def list_company_info(db: AsyncSession):
    try:
        company_info_list = await db.execute(select(CompanyInfo))
        company_info_list = company_info_list.scalars().all()
        
        company_info_data = [CompanyInfoRead.model_validate(company_info).model_dump() for company_info in company_info_list]
        logger.info("Retrieved Company Info list")
        return success_response(data=company_info_data, message="Company Info list retrieved successfully")

    except Exception as e:
        logger.error(f"Failed to get company info list: {str(e)}")
        return internal_server_error(f"Failed to get company info list: {str(e)}")

async def get_company_info(db: AsyncSession, company_info_id: UUID):
    try:
        company_info = await db.get(CompanyInfo, company_info_id)

        if not company_info:
            logger.warning("Company Info not found", extra={"company_info_id": str(company_info_id)})
            return HTTPException(status_code=404, detail="Company Info not found")

        company_info_data = CompanyInfoRead.model_validate(company_info).model_dump()
        logger.info("Retrieved Company Info", extra={"company_info_id": str(company_info_id)})
        return success_response(data=company_info_data, message="Company Info retrieved successfully")
    
    except Exception as e:
        logger.error(f"Failed to get company info:{str(e)}")
        return internal_server_error(f"Failed to get company info: {str(e)}")


async def update_company_info(db: AsyncSession, company_info_id: UUID, data: CompanyInfoUpdate):
    try:
        company_info = await db.get(CompanyInfo, company_info_id)

        if company_info is None:
            logger.warning("Company Info not found for update", extra={"company_info_id": str(company_info_id)})
            return HTTPException(status_code=404, detail="Company Info not found")

        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Company Info update data", company_size=str(data.company_size), update_data=update_data)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(company_info, field, value)

       
        await db.commit()
        await db.refresh(company_info)

        company_info_data = CompanyInfoRead.model_validate(company_info).model_dump()
        logger.info("Updated Company Info", extra={"company_info_id": str(company_info_id)})
        return success_response(data=company_info_data, message="Company Info updated successfully")
    
    except Exception as e:
        logger.error(f"Failed to update company info:{str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to update company info: {str(e)}")