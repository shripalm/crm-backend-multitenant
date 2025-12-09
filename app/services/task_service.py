from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.task_table import Task
from app.models.users import User
from app.schemas.task_schema import TaskRead, TaskUpdate
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)

from app.utils.logging import logger
from app.services.task_workflow_service import crm_data_leads_wf_definition, interested_func, callback_func, lead_drop_func

async def list_tasks_for_user(db: AsyncSession, user_id: UUID):
    """List all tasks assigned to a specific user.

    The Task table stores the assignee in the `assigned_to` field as a string.
    We resolve the user by `user_id` and then match tasks where
    `Task.assigned_to` equals the user's `full_name`.
    """
    try:
        user = await db.get(User, user_id)
        if user is None:
            logger.warning("User not found while listing tasks", user_id=str(user_id))
            return error_response(404, "User not found")

        stmt = (
            select(Task)
            .where(Task.assigned_to == user.full_name)
            .order_by(Task.created_at.desc())
        )
        logger.debug(
            "Task listing query",
            user_id=str(user_id),
            assignee=user.full_name,
        )
        result = await db.execute(stmt)
        tasks = result.scalars().all()

        data = [TaskRead.model_validate(t).model_dump() for t in tasks]
        logger.debug("Listed tasks for user", user_id=str(user_id), count=len(data))
        return success_response(data=data, message="Tasks retrieved")

    except Exception as e:
        logger.error(f"Failed to list tasks for user {user_id}: {str(e)}")
        return internal_server_error(f"Failed to list tasks for user: {str(e)}")

async def update_task_for_user(db: AsyncSession, task_id: UUID, data: TaskUpdate):
    """Update a specific task for a user, focusing on status and callback_time."""
    try:
        if data.status is None:
            logger.warning("Task update missing status", task_id=str(task_id))
            return error_response(400, "Status is required for update")
       
        task = await db.get(Task, task_id)
        if task is None:
            logger.warning("Task not found for update", task_id=str(task_id))
            return error_response(404, "Task not found")
        
        # Keep both the pydantic model and a plain dict for downstream workflows
        task_model = TaskRead.model_validate(task)
        task_data = task_model.model_dump()

        # Now route based on status (use string lower for safe comparisons)
        status = data.status.strip().lower()
        logger.info("Updating task status", task_id=str(task_id), status=status)
        logger.debug(
            "Task workflow routing",
            task_id=str(task_id),
            status=status,
            payload=task_data,
        )
        if status == "interested":
            return await interested_func(
                db,
                action={
                    "models": {"task": task_data},
                    "data": {"remarks": data.remarks},
                },
            )
        elif status == "callback":
            return await callback_func(
                db,
                action={
                    "models": {"task": task_data},
                    "data": {**data.model_dump(), "testing_field": "testing_value"},
                },
            )
        elif status == "not interested":
            return await lead_drop_func(db, 
                action={
                    "models": {"task": task_data},
                    "data": {**data.model_dump(), "testing_field": "testing_value"},
                }
            )
        else:
            return error_response(400, "Invalid status value")

    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {str(e)}")
        return internal_server_error(f"Failed to update task: {str(e)}")
