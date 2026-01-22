from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models.core_team import CoreTeam
from app.schemas.core_team import CoreTeam as CoreTeamSchema, CoreTeamCreate

router = APIRouter()

@router.post("/", response_model=CoreTeamSchema, status_code=status.HTTP_201_CREATED)
async def create_core_team(
    core_team_in: CoreTeamCreate,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Create a new Core Team member.
    """
    core_team = CoreTeam(
        name=core_team_in.name,
        number=core_team_in.number,
    )
    db.add(core_team)
    await db.commit()
    await db.refresh(core_team)
    return core_team

@router.get("/", response_model=List[CoreTeamSchema])
async def read_core_teams(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Retrieve Core Team members.
    """
    stmt = select(CoreTeam).offset(skip).limit(limit)
    result = await db.execute(stmt)
    core_teams = result.scalars().all()
    return core_teams
