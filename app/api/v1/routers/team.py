from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.team_schema import TeamCreate, TeamRead
from app.services.team_service import create_team, list_teams

router = APIRouter()


@router.post("/", response_model=TeamRead)
async def add_team(payload: TeamCreate, db: AsyncSession = Depends(get_db)):
    return await create_team(db, payload)


@router.get("/", response_model=list[TeamRead])
async def get_teams(db: AsyncSession = Depends(get_db)):
    return await list_teams(db)
