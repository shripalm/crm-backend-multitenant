from typing import Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.teams import Team
from app.schemas.team_schema import TeamRead
from app.utils.response import success_response, internal_server_error


async def create_team(db: AsyncSession, data: Any):
    """Create a Team and return serialized response."""
    try:
        team = Team(name=data.name, description=data.description)
        db.add(team)
        await db.commit()
        await db.refresh(team)

        team_data = TeamRead.model_validate(team).model_dump()
        return success_response(data=team_data, message="Team created")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to create team: {str(e)}")


async def list_teams(db: AsyncSession) -> List[dict]:
    try:
        result = await db.execute(select(Team))
        teams = result.scalars().all()
        data = [TeamRead.model_validate(t).model_dump() for t in teams]
        return success_response(data=data, message="Teams retrieved")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to list teams: {str(e)}")
