from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.schemas.booking_schema import BookingCreate, BookingRead
from app.services.bookings_service import (
    create_booking,
    list_bookings,
    update_booking,
    get_booking
)   

router = APIRouter()

# Create a new booking
@router.post("/", response_model = StandardResponse[BookingRead])
async def add_booking(payload: BookingCreate, db:AsyncSession = Depends(get_db)):
    """Create a new booking"""
    return await create_booking(db, payload)

# List all bookings
@router.get("/", response_model=StandardResponse[list[BookingRead]])
async def get_bookings(db: AsyncSession = Depends(get_db)):
    """Retrieve a list of all bookings"""
    return await list_bookings(db)

# Get a single booking by ID
@router.get("/{booking_id}", response_model=StandardResponse[BookingRead])
async def get_booking_by_id(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single booking by ID"""
    return await get_booking(db, booking_id)

# Update an existing booking
@router.put("/{booking_id}", response_model=StandardResponse[BookingRead])
async def update_booking_by_id(
    booking_id: UUID, payload: BookingCreate, db: AsyncSession = Depends(get_db)):
    """Update an existing booking"""
    return await update_booking(db, booking_id, payload)    