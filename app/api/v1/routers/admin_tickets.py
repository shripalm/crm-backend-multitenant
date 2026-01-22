from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.admin_session import get_admin_db
from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.services.ticket_service import (
    list_admin_agent_panel_tickets,
    list_admin_user_panel_tickets,
    update_ticket_category,
)

router = APIRouter()


@router.get("/agent", response_model=StandardResponse[list[dict]])
async def get_agent_panel_tickets(db: AsyncSession = Depends(get_admin_db)):
    return await list_admin_agent_panel_tickets(db)


@router.get("/user", response_model=StandardResponse[list[dict]])
async def get_user_panel_tickets(
    db: AsyncSession = Depends(get_admin_db),
    user_db: AsyncSession = Depends(get_db),
):
    return await list_admin_user_panel_tickets(db, user_db)


@router.patch("/category/{ticket_id}", response_model=StandardResponse[dict])
async def change_ticket_category(
    ticket_id: str,
    new_category: str,
    db: AsyncSession = Depends(get_admin_db),
):
    return await update_ticket_category(db, ticket_id, new_category)
