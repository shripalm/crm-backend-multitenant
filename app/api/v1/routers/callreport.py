from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date
from typing import Optional

from app.db.session import get_db
from app.schemas.callreport_schema import CallReportCreate, CallReportRead, CallReportUpdate
from app.schemas.response import StandardResponse
from app.services.callreport_service import (
    create_call_report,
    list_call_reports,
    get_call_report_stats,
    get_call_report,  
    update_call_report,
    delete_call_report,
)
from app.utils.pagination import PaginationParams
router = APIRouter()


@router.post("/", response_model=StandardResponse[CallReportRead])
async def add_call_report(payload: CallReportCreate, db: AsyncSession = Depends(get_db)):
    """Create a new call report"""
    return await create_call_report(db, payload)


@router.get("/", response_model=StandardResponse)
async def get_call_reports(
    page: int = Query(1, description="Page number (starts from 1)"),
    size: int = Query(20, description="Items per page (max 100)"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_direction: Optional[str] = Query("desc", description="Sort direction (asc or desc)"),
    db: AsyncSession = Depends(get_db),
):
    """Get all call reports with pagination"""
    pagination_params = PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_direction=sort_direction.lower() if sort_direction else "desc",
    )
    return await list_call_reports(db, pagination_params)


@router.get("/stats", response_model=StandardResponse)
async def get_call_report_statistics(
    date_from: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    employee_id: Optional[UUID] = Query(None, description="Filter by employee/user id"),
    db: AsyncSession = Depends(get_db),
):
    """Get call count stats grouped by employee (kis user ne kitne calls kiye)."""
    return await get_call_report_stats(db, date_from=date_from, date_to=date_to, employee_id=employee_id)


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
