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


async def list_tasks_for_user(db: AsyncSession, user_id: UUID):
    """List all tasks assigned to a specific user.

    The Task table stores the assignee in the `assigned_to` field as a string.
    We resolve the user by `user_id` and then match tasks where
    `Task.assigned_to` equals the user's `full_name`.
    """
    try:
        user = await db.get(User, user_id)
        if user is None:
            return error_response(404, "User not found")

        stmt = (
            select(Task)
            .where(Task.assigned_to == user.full_name)
            .order_by(Task.created_at.desc())
        )
        result = await db.execute(stmt)
        tasks = result.scalars().all()

        data = [TaskRead.model_validate(t).model_dump() for t in tasks]
        return success_response(data=data, message="Tasks retrieved")

    except Exception as e:
        return internal_server_error(f"Failed to list tasks for user: {str(e)}")


async def update_task_for_user(db: AsyncSession, user_id: UUID, task_id: UUID, data: TaskUpdate):
    """Update a specific task for a user, focusing on status and callback_time.

    This keeps alignment with the existing pattern where Task.assigned_to
    stores the user's full_name. It also ensures that when status is
    "Callback", a callback_time can be set, and when status is
    "Not Interested", the status is saved as-is and callback_time is cleared.
    """
    try:
        user = await db.get(User, user_id)
        if user is None:
            return error_response(404, "User not found")

        task = await db.get(Task, task_id)
        if task is None:
            return error_response(404, "Task not found")

        # Ensure the task belongs to this user based on assigned_to convention
        if task.assigned_to != user.full_name:
            return error_response(403, "Task does not belong to this user")

        # Apply updates only for provided fields
        if data.status is not None:
            task.status = data.status

            # When status is Not Interested, clear callback_time
            if data.status == "Not Interested":
                task.callback_time = None

        # For Callback status, allow setting callback_time explicitly
        if data.callback_time is not None:
            task.callback_time = data.callback_time

        # Optional: remarks or other fields can still be updated via TaskUpdate
        if data.remarks is not None:
            task.remarks = data.remarks

        await db.commit()
        await db.refresh(task)

        task_data = TaskRead.model_validate(task).model_dump()
        return success_response(data=task_data, message="Task updated")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to update task: {str(e)}")
