from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Project
from app.schemas.project_schema import ProjectCreate, ProjectRead
from app.utils.response import success_response, created_response, internal_server_error, error_response
from app.utils.logging import logger
from app.utils.pagination import (
    PaginationParams,
    PaginatedResponse,
    get_paginator,
    T
)


from app.schemas.project_creation_payload import ProjectWithIncentiveCreate

async def create_project(db: AsyncSession, project_in: ProjectWithIncentiveCreate):
    """
    Create a new Project record with incentive handling.
    Uses ProjectWithIncentiveCreate to keep project and incentive data separate.
    """
    try:
        # Import here to avoid circular imports
        from app.services.incentive_service import create_project_incentive_config, copy_default_to_project
        
        # Extract project data and incentive options
        project_data = project_in.project_data
        add_incentives = project_in.add_incentives
        incentive_config = project_in.incentive_config
        
        # Create project using the base project data
        payload = project_data.dict(exclude_none=True)
        logger.info("Creating project", payload=payload)
        logger.debug("Project payload", payload=payload)
        
        project = Project(**payload)
        db.add(project)
        await db.commit()
        await db.refresh(project)
        
        # Handle incentive configuration independently
        try:
            if add_incentives and incentive_config:
                # Option 1: Add custom incentives
                logger.info("Creating custom incentive config for project", project_id=str(project.id))
                await create_project_incentive_config(db, project.id, incentive_config)
            else:
                # Option 2: Skip incentives - Copy default configuration
                logger.info("Copying default incentive config to project", project_id=str(project.id))
                await copy_default_to_project(db, project.id)
            
        except Exception as incentive_error:
            # If incentive creation fails, log the error but the project exists
            logger.error(f"Failed to create incentive config for project {project.id}: {str(incentive_error)}")
        
        logger.info("Project created successfully", project_id=str(project.id))
        return created_response(
            data=ProjectRead.from_orm(project).dict(), 
            message="Project created successfully with incentive configuration"
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create project: {str(e)}")
        return internal_server_error(f"Failed to create project: {str(e)}")


async def list_projects(
    db: AsyncSession,
    pagination_params: PaginationParams,
):
    """Return a standardized success response containing list of projects with pagination."""
    try:
        paginator = get_paginator(db)
        query = select(Project).where(Project.is_deleted == False).order_by(Project.created_at.desc())
        result = await paginator.paginate(
            query=query,
            pagination_params=pagination_params,
            model_class=Project
        )
        projects_data = [ProjectRead.from_orm(p).dict() for p in result.data]
        paginated_response = PaginatedResponse[ProjectRead](
            data=projects_data,
            meta=result.meta,
            message="Projects fetched"
        )
        return success_response(data=paginated_response.model_dump(), message="Projects fetched")
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        return internal_server_error(f"Failed to list projects: {str(e)}")
    

async def soft_delete_project(db: AsyncSession, project_id: str):
    try:
        project = await db.get(Project, project_id)
        if not project:
            logger.warning("Project not found for soft delete", project_id=project_id)
            return error_response(404, "Project not found")

        project.is_deleted = True
        await db.commit()
        await db.refresh(project)

        logger.info("Project soft deleted", project_id=project_id)
        logger.debug("Project soft delete state", project_id=project_id, is_deleted=project.is_deleted)
        return success_response(message="Project soft deleted", data={})
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to soft delete project: {str(e)}")
        return internal_server_error(str(e))


async def hard_delete_project(db: AsyncSession, project_id: str):
    try:
        project = await db.get(Project, project_id)
        if not project:
            logger.warning("Project not found for hard delete", project_id=project_id)
            return None

        await db.delete(project)
        await db.commit()

        logger.info("Project hard deleted", project_id=project_id)
        return success_response(message="Project permanently deleted", data={})
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to hard delete project: {str(e)}")
        return internal_server_error(str(e))

