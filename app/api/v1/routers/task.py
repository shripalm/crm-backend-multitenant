from uuid import UUID
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.task_schema import TaskRead, TaskUpdate
from app.schemas.response import StandardResponse
from app.services.task_service import (
    list_tasks_for_user,
    update_task_for_user,
    list_all_tasks,
)
from app.services.search_filter_service import search_tasks


router = APIRouter()


@router.get("/list/{user_id}", response_model=StandardResponse[list[dict]])
async def get_tasks_for_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await list_tasks_for_user(db, user_id)
    
@router.get("/search", response_model=StandardResponse[list[TaskRead]])
async def search_tasks_endpoint(
    project: Optional[str] = Query(None, description="Filter by Project Name"),
    activity_type: Optional[str] = Query(None, description="Filter by Activity Type"),
    start_date: Optional[datetime] = Query(None, description="Filter by Start Date (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Filter by End Date (YYYY-MM-DD)"),
    team: Optional[str] = Query(None, description="Filter by Team Name"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by Assigned User ID"),
    status: Optional[str] = Query(None, description="Filter by Task Status"),
    assigned_by: Optional[UUID] = Query(None, description="Filter by Assigned By User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search tasks with multiple filters.
    """
    return await search_tasks(
        db=db,
        project=project,
        activity_type=activity_type,
        start_date=start_date,
        end_date=end_date,
        team=team,
        assigned_to=assigned_to,
        status=status,
        assigned_by=assigned_by
    )

@router.patch("/update/{task_id}", response_model=StandardResponse)
async def update_task_for_user_endpoint(
    task_id: UUID,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a task's status and callback_time for a specific user.

    This does not add full CRUD for tasks; it just lets clients set
    statuses like "Not Interested" or "Callback" and, in the case of
    "Callback", provide a callback_time value.
    """
    return await update_task_for_user(db, task_id, payload)


@router.get("/all", response_model=StandardResponse[list[dict]])
async def get_all_tasks(db: AsyncSession = Depends(get_db)):
    return await list_all_tasks(db)
