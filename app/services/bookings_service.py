from http.client import HTTPException
from typing import Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete   
from sqlalchemy.orm import selectinload
from app.utils.logging import logger
from app.models.bookings import Booking
from app.schemas.booking_schema import BookingCreate, BookingRead, BookingUpdate    
from app.utils.response import (
    success_response,       
    error_response,
    internal_server_error,
)
from app.utils.pagination import (
    PaginationParams,
    PaginatedResponse,
    get_paginator,
    T
)


async def create_booking(db: AsyncSession, data: BookingCreate):
    try:
        logger.info("Creating Booking", booking_date=str(data.booking_date))
        booking = Booking(
            booking_date = data.booking_date,
            payment_status = data.payment_status,
            payment_paid = data.payment_paid,
            payment_mode = data.payment_mode,
            last_follow_up = data.last_follow_up,
            stage = data.stage,
        )

        db.add(booking)
        await db.commit()
        await db.refresh(booking)

        booking_data = BookingRead.model_validate(booking).model_dump()
        logger.info("Booking created successfully", booking_id = str(booking.booking_id))
        return success_response(data=booking_data, message="Booking created successfully")

    except Exception as e:
        logger.error(f"Failed to create booking:{str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to create booking:{str(e)}")
    
async def list_bookings(
    db: AsyncSession,
    pagination_params: PaginationParams,
):
    """List all bookings and return serialized response."""
    try:
        paginator = get_paginator(db)
        query = select(Booking).order_by(Booking.booking_date.desc())
        result = await paginator.paginate(
            query=query,
            pagination_params=pagination_params,
            model_class=Booking
        )
        bookings_data = [BookingRead.model_validate(bk).model_dump() for bk in result.data]
        paginated_response = PaginatedResponse[BookingRead](
            data=bookings_data,
            meta=result.meta,
            message="Bookings retrieved successfully"
        )
        return success_response(data=paginated_response.model_dump(), message="Bookings retrieved successfully")
    except Exception as e:
        logger.error(f"Failed to list bookings:{str(e)}")
        return internal_server_error(f"Failed to list bookings: {str(e)}")
    

async def get_booking(db: AsyncSession, booking_id: UUID):
    try:
        booking = await db.get(Booking, booking_id)
        if not booking:
            logger.warning("Booking not foung", extra ={"booking id": str(booking_id)}
            )
            raise HTTPException(status_code=404, detail="Booking not found")            
        
        booking_data = BookingRead.model_validate(booking).model_dump()
        
        logger.info("Booking retrieved successfully", booking_id=str(booking_id))
        
        return success_response(data=booking_data, message="Booking retrieved successfully")
    except HTTPException:
        raise   
    except Exception as e:
        logger.error(f"Failed to get booking: {str(e)}", extra={"booking_id": str(booking_id)})
        return HTTPException(status_code=500, detail=f"Failed to get booking: {str(e)}")    
    
async def update_booking(db: AsyncSession, booking_id: UUID, data: BookingUpdate):
    try:
        booking = await db.get(Booking, booking_id)
        
        if booking is None:
            logger.warning("Booking not found for update", booking_id=str(booking_id))
            return error_response(404, "Booking not found for update")
        
        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Updating booking", booking_id=str(booking_id), update_data=update_data)   

        for field, value in update_data.items():
            setattr(booking, field, value)

        await db.commit()
        await db.refresh(booking)

        booking_data = BookingRead.model_validate(booking).model_dump()
        logger.info("Booking updated successfully", booking_id=str(booking_id))     
        return success_response(data=booking_data, message="Booking updated successfully")

    except Exception as e:
        logger.error(f"Failed to update booking: {str(e)}", extra={"booking_id": str(booking_id)})
        await db.rollback()
        return internal_server_error(f"Failed to update booking: {str(e)}")
