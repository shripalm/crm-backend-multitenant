import uuid
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.invoice import Invoice
from app.enums.payment_enums import InvoiceStatus
from app.utils.logging import logger

async def create_invoice_for_booking(
    db: AsyncSession,
    booking_id: uuid.UUID,
    amount: float,
    description: Optional[str] = None
) -> Optional[Invoice]:
    """
    Create a new invoice for a booking.
    
    Args:
        db: Database session
        booking_id: ID of the booking
        amount: Invoice amount
        description: Optional description
        
    Returns:
        Created Invoice object or None if failed
    """
    try:
        # Generate a unique invoice number
        # Format: INV-YYYYMMDD-XXXX (where XXXX is random hex)
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%md")
        random_suffix = uuid.uuid4().hex[:4].upper()
        invoice_no = f"INV-{date_str}-{random_suffix}"
        
        invoice = Invoice(
            invoice_no=invoice_no,
            booking_id=booking_id,
            amount=Decimal(str(amount)),
            status=InvoiceStatus.CREATED,
            description=description or f"Invoice for booking {booking_id}"
        )
        
        db.add(invoice)
        await db.flush()
        
        logger.info(
            "Invoice created for booking",
            booking_id=str(booking_id),
            invoice_no=invoice_no,
            amount=amount
        )
        
        return invoice
        
    except Exception as e:
        logger.error(f"Failed to create invoice for booking: {str(e)}", extra={"booking_id": str(booking_id)})
        return None
