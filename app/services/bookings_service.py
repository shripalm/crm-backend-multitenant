from http.client import HTTPException
from typing import Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete   
from sqlalchemy.orm import selectinload
from app.utils.logging import logger
from app.models.bookings import Booking
from app.models.sitevisit import SiteVisit
from app.models.contact import Contact
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


def calculate_payable_amount(budget_range: Optional[str] = None) -> float:
    """
    Calculate payable amount based on contact's budget range.

    Args:
        budget_range: Budget range string like "50L-1Cr", "1Cr-2Cr"

    Returns:
        Calculated amount in rupees
    """
    # Default amount if no budget info available
    default_amount = 5000000.0  # 50 lakhs

    if not budget_range:
        return default_amount

    # Parse budget range and calculate approximate amount
    # Example ranges: "50L-1Cr", "1Cr-2Cr", "2Cr-3Cr"
    try:
        range_lower = budget_range.lower()

        if "50l-1cr" in range_lower:
            return 7500000.0  # 75 lakhs (midpoint)
        elif "1cr-2cr" in range_lower:
            return 15000000.0  # 1.5 crores (midpoint)
        elif "2cr-3cr" in range_lower:
            return 25000000.0  # 2.5 crores (midpoint)
        elif "3cr+" in range_lower:
            return 35000000.0  # 3.5 crores (minimum)
        else:
            # Try to extract numeric values
            import re
            numbers = re.findall(r'\d+', range_lower)
            if numbers:
                # Convert lakhs/crores to rupees
                if "cr" in range_lower:
                    return float(numbers[0]) * 10000000  # crores to rupees
                elif "l" in range_lower:
                    return float(numbers[0]) * 100000  # lakhs to rupees
    except Exception:
        pass

    return default_amount


async def get_budget_range_from_site_visit(db: AsyncSession, site_visit_id: Optional[UUID]) -> Optional[str]:
    """
    Get budget range from contact associated with site visit.

    Args:
        db: Database session
        site_visit_id: Site visit ID

    Returns:
        Budget range string or None
    """
    if not site_visit_id:
        return None

    try:
        stmt = select(SiteVisit).options(selectinload(SiteVisit.contact)).where(SiteVisit.id == site_visit_id)
        result = await db.execute(stmt)
        site_visit = result.scalar_one_or_none()

        if site_visit and site_visit.contact:
            return site_visit.contact.budget_range

    except Exception as e:
        logger.warning(f"Failed to get budget range from site visit: {str(e)}")

    return None


async def create_booking(db: AsyncSession, data: BookingCreate):
    try:
        logger.info("Creating Booking", booking_date=str(data.booking_date))

        # Calculate payable amount based on contact's budget range
        budget_range = await get_budget_range_from_site_visit(db, data.site_visit_id)
        payable_amount = calculate_payable_amount(budget_range)

        logger.info(
            "Calculated payable amount",
            amount=payable_amount,
            budget_range=budget_range
        )

        # Create booking
        booking = Booking(
            booking_date=data.booking_date,
            last_follow_up=data.last_follow_up,
            stage=data.stage,
            due_date=data.due_date,
            site_visit_id=data.site_visit_id,
            payment_status=data.payment_status,
            payment_paid=data.payment_paid,
            payment_mode=data.payment_mode,
            core_team_id=data.core_team_id,
            project_id=data.project_id,
            property_id=data.property_id,
        )

        db.add(booking)
        await db.commit()
        await db.refresh(booking)

        # Prepare response
        booking_data = BookingRead.model_validate(booking).model_dump()

        logger.info(
            "Booking created successfully",
            booking_id=str(booking.booking_id)
        )

        return success_response(
            data=booking_data,
            message="Booking created successfully"
        )

    except Exception as e:
        logger.error(f"Failed to create booking: {str(e)}")
        await db.rollback()
        return internal_server_error(f"Failed to create booking: {str(e)}")
    
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
