from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.admin_session import get_admin_db
from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.schemas.ticket_schema import AgentTicketCreate, AgentTicketRead, TicketRead
from app.services.ticket_service import create_agent_ticket, list_agent_tickets

router = APIRouter()


@router.post("/", response_model=StandardResponse[TicketRead])
async def raise_ticket(
    payload: AgentTicketCreate,
    db: AsyncSession = Depends(get_admin_db),
):
    return await create_agent_ticket(db, payload)


@router.get("/", response_model=StandardResponse[list[AgentTicketRead]])
async def get_tickets(
    db: AsyncSession = Depends(get_admin_db),
    user_db: AsyncSession = Depends(get_db),
):
    return await list_agent_tickets(db, user_db)
