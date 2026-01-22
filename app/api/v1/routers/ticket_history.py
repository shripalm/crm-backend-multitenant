from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.admin_session import get_admin_db
from app.schemas.response import StandardResponse
from app.schemas.ticket_status_history_schema import TicketStatusHistoryRead
from app.services.ticket_service import list_ticket_history

router = APIRouter()


@router.get("/history/{ticket_id}", response_model=StandardResponse[list[TicketStatusHistoryRead]])
async def get_ticket_history(ticket_id: UUID, db: AsyncSession = Depends(get_admin_db)):
    return await list_ticket_history(db, ticket_id)
