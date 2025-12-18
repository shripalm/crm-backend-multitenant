from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.schemas.callreport_schema import CallReportCreate, CallReportRead, CallReportUpdate
from app.schemas.response import StandardResponse
from app.services.callreport_service import (
    create_call_report,
    list_call_reports,
    get_call_report,  
    update_call_report,
    delete_call_report,
)

router = APIRouter()


@router.post("/", response_model=StandardResponse[CallReportRead])
async def add_call_report(payload: CallReportCreate, db: AsyncSession = Depends(get_db)):
    """Create a new call report"""
    return await create_call_report(db, payload)


@router.get("/", response_model=StandardResponse[list[dict]])
async def get_call_reports(db: AsyncSession = Depends(get_db)):
    """Get all call reports"""
    return await list_call_reports(db)


@router.get("/{call_report_id}", response_model=StandardResponse[dict])
async def get_call_report_by_id(call_report_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single call report by ID"""
    return await get_call_report(db, call_report_id)


@router.put("/{call_report_id}", response_model=StandardResponse[CallReportRead])
async def update_call_report_by_id(
    call_report_id: UUID, payload: CallReportUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an existing call report"""
    return await update_call_report(db, call_report_id, payload)


@router.delete("/{call_report_id}", response_model=StandardResponse)
async def delete_call_report_by_id(call_report_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a call report"""
    return await delete_call_report(db, call_report_id)
