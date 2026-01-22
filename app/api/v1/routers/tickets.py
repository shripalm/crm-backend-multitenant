from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.admin_session import get_admin_db
from app.schemas.response import StandardResponse
from app.schemas.ticket_schema import TicketStatusUpdate, TicketRead, UserTicketCreate
from app.services.ticket_service import update_ticket_status_and_comment, create_user_ticket
from app.middleware.client_middleware import get_current_user

router = APIRouter()


@router.patch("/update/{ticket_id}", response_model=StandardResponse[TicketRead])
async def update_ticket(
    ticket_id: UUID,
    payload: TicketStatusUpdate,
    db: AsyncSession = Depends(get_admin_db),
):
    return await update_ticket_status_and_comment(db, ticket_id, payload)


@router.post("/user", response_model=StandardResponse[TicketRead])
async def raise_user_ticket(
    payload: UserTicketCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_admin_db),
):
    return await create_user_ticket(db, current_user, payload)
