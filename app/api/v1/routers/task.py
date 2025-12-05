from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.task_schema import TaskRead, TaskUpdate
from app.schemas.response import StandardResponse
from app.services.task_service import (
    list_tasks_for_user,
    update_task_for_user,
)


router = APIRouter()


@router.get("/list/{user_id}", response_model=StandardResponse[list[TaskRead]])
async def get_tasks_for_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await list_tasks_for_user(db, user_id)
    
@router.get("/search", response_model=StandardResponse[list[TaskRead]])
async def get_tasks_for_user(
    user_id: UUID = Query(..., description="User ID to filter tasks for"),
    db: AsyncSession = Depends(get_db)
):
    return await list_tasks_for_user(db, user_id)

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
