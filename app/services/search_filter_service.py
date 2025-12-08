from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.task_table import Task
from app.models.contact import Contact
from app.models.users import User
from app.schemas.task_schema import TaskRead
from app.utils.response import success_response, internal_server_error
from app.utils.logger import logger

async def search_tasks(
    db: AsyncSession,
    project: Optional[str] = None,
    activity_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    team: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    status: Optional[str] = None,
    assigned_by: Optional[UUID] = None,
):
    """
    Search tasks with multiple filters.
    
    Mappings:
    - project -> Contact.project_name (via Task.lead_id)
    - team -> Task.assigned_to_team
    - assigned_to -> Task.assigned_to (Resolved from UUID to User.full_name)
    - status -> Task.status
    - date_range -> Task.created_at (start_date, end_date)
    """
    try:
        logger.info("Searching tasks with filters: project=%s, team=%s, assigned_to=%s, status=%s, start_date=%s, end_date=%s", project, team, assigned_to, status, start_date, end_date)
        # Start with a join to Contact to allow filtering by project
        stmt = select(Task).join(Contact, Task.lead_id == Contact.id, isouter=True)

        conditions = []

        # Filter by Project (on Contact model)
        if project:
            conditions.append(Contact.project_name == project)
        
        # Filter by Team
        if team:
            conditions.append(Task.assigned_to_team == team)
            
        # Filter by Status
        if status:
            conditions.append(Task.status == status)
            
        # Filter by Date Range (Created At)
        if start_date:
            conditions.append(Task.created_at >= start_date)
        if end_date:
            conditions.append(Task.created_at <= end_date)
            
        # Filter by Assigned To (Direct UUID comparison)
        if assigned_to:
            conditions.append(Task.assigned_to == assigned_to)

        # Filter by Assigned By (Direct UUID comparison)
        if assigned_by:
            conditions.append(Task.assigned_by == assigned_by)

            
        # Note: 'activity_type' is not currently present in the Task model.
        # They are included in the interface as requested but won't apply DB filters yet.
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
            
        # Order by newest first
        stmt = stmt.order_by(Task.created_at.desc())
        
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        logger.debug("Tasks retrieved: %s", tasks)
        
        data = [TaskRead.model_validate(t).model_dump() for t in tasks]
        logger.info("Tasks retrieved successfully: %s", data)
        return success_response(data=data, message="Tasks retrieved successfully")
        
    except Exception as e:
        logger.error("Failed to search tasks: %s", str(e))
        return internal_server_error(f"Failed to search tasks: {str(e)}")
