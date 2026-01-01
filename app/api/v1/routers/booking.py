from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.schemas.booking_schema import BookingCreate, BookingRead, BookingUpdate
from app.services.bookings_service import (
    create_booking,
    list_bookings,
    update_booking,
    get_booking
)   
from app.utils.pagination import PaginationParams

router = APIRouter()

# Create a new booking
@router.post("/", response_model = StandardResponse[BookingRead])
async def add_booking(payload: BookingCreate, db:AsyncSession = Depends(get_db)):
    """Create a new booking"""
    return await create_booking(db, payload)

# List all bookings
@router.get("/", response_model=StandardResponse)
async def get_bookings(
    page: int = Query(1, description="Page number (starts from 1)"),
    size: int = Query(20, description="Items per page (max 100)"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_direction: Optional[str] = Query("desc", description="Sort direction (asc or desc)"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a list of all bookings with pagination"""
    pagination_params = PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_direction=sort_direction.lower() if sort_direction else "desc",
    )
    return await list_bookings(db, pagination_params)

# Get a single booking by ID
@router.get("/{booking_id}", response_model=StandardResponse[BookingRead])
async def get_booking_by_id(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single booking by ID"""
    return await get_booking(db, booking_id)

# Update an existing booking
@router.put("/{booking_id}", response_model=StandardResponse[BookingRead])
async def update_booking_by_id(
    booking_id: UUID, payload: BookingUpdate, db: AsyncSession = Depends(get_db)):
    """Update an existing booking"""
    return await update_booking(db, booking_id, payload)