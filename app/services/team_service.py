from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.teams import Team 


async def create_team(db: AsyncSession, data):
    team = Team(name=data.name, description=data.description)
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


async def list_teams(db: AsyncSession):
    result = await db.execute(select(Team))
    return result.scalars().all()
