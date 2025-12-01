from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Project
from app.schemas.project_schema import ProjectCreate, ProjectRead
from app.utils.response import success_response, internal_server_error, error_response


async def create_project(db: AsyncSession, project_in: ProjectCreate):
    """Create a new Project record and return standardized response."""
    try:
        payload = project_in.dict(exclude_none=True)
        project = Project(**payload)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        return success_response(data=ProjectRead.from_orm(project).dict(), message="Project created")
    except Exception as e:
        # Attempt rollback if possible
        try:
            await db.rollback()
        except Exception:
            pass
        return internal_server_error(f"Failed to create project: {str(e)}")


async def list_projects(db: AsyncSession, limit: int = 100, offset: int = 0):
    """Return a standardized success response containing list of projects."""
    try:
        stmt = select(Project).where(Project.is_deleted == False).limit(limit).offset(offset)
        result = await db.execute(stmt)
        projects = result.scalars().all()
        data = [ProjectRead.from_orm(p).dict() for p in projects]
        return success_response(data=data, message="Projects fetched")
    except Exception as e:
        return internal_server_error(f"Failed to list projects: {str(e)}")
    

async def soft_delete_project(db: AsyncSession, project_id: str):
    try:
        project = await db.get(Project, project_id)
        if not project:
            return error_response(404, "Project not found")

        project.is_deleted = True
        await db.commit()
        await db.refresh(project)

        return success_response(message="Project soft deleted", data={})
    except Exception as e:
        await db.rollback()
        return internal_server_error(str(e))


async def hard_delete_project(db: AsyncSession, project_id: str):
    try:
        project = await db.get(Project, project_id)
        if not project:
            return None

        await db.delete(project)
        await db.commit()

        return success_response(message="Project permanently deleted", data={})
    except Exception as e:
        await db.rollback()
        return internal_server_error(str(e))

