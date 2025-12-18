from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.task_table import Task
from app.models.users import User
from app.models.contact import Contact
from app.schemas.task_schema import TaskRead, TaskUpdate
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)

from app.services.task_workflow_service import crm_data_leads_wf_definition, interested_func, callback_func, lead_drop_func

async def list_all_tasks(db: AsyncSession):
    """List all tasks in the system."""
    try:
        stmt = (
            select(Task, User, Contact)
            .join(User, Task.assigned_to == User.id, isouter=True)
            .join(Contact, Task.lead_id == Contact.id, isouter=True)
            .order_by(Task.created_at.desc())
        )

        result = await db.execute(stmt)
        rows = result.unique().all()

        data: list[dict[str, Any]] = []
        for task, user, contact in rows:
            item = {
                "id": str(task.id),
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "status": task.status,
                # Replace foreign keys with related names
                "assigned_to": user.full_name if user else None,
                "assigned_to_team": task.assigned_to_team,
                "assigned_by": str(task.assigned_by) if task.assigned_by else None,
                "remarks": task.remarks,
                "callback_time": task.callback_time,
                "lead_id": contact.name if contact else None,
                "contact_no": contact.contact_no if contact else None,
            }
            data.append(item)
        return success_response(data=data, message="All tasks retrieved")
    except Exception as e:
        return internal_server_error(f"Failed to list all tasks: {str(e)}")

async def list_tasks_for_user(db: AsyncSession, user_id: UUID):
    """List all tasks assigned to a specific user.

    The Task table stores the assignee in the `assigned_to` field as a UUID.
    We resolve the user by `user_id` and then match tasks where
    `Task.assigned_to` equals the user's `id`.
    """
    try:
        user = await db.get(User, user_id)
        if user is None:
            return error_response(404, "User not found")

        stmt = (
            select(Task, User, Contact)
            .join(User, Task.assigned_to == User.id, isouter=True)
            .join(Contact, Task.lead_id == Contact.id, isouter=True)
            .where(Task.assigned_to == user_id)
            .order_by(Task.created_at.desc())
        )

        result = await db.execute(stmt)
        rows = result.unique().all()

        data: list[dict[str, Any]] = []
        for task, user_row, contact in rows:
            item = {
                "id": str(task.id),
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "status": task.status,
                # Replace foreign keys with related names
                "assigned_to": user_row.full_name if user_row else None,
                "assigned_to_team": task.assigned_to_team,
                "assigned_by": str(task.assigned_by) if task.assigned_by else None,
                "remarks": task.remarks,
                "callback_time": task.callback_time,
                "lead_id": contact.name if contact else None,
                "contact_no": contact.contact_no if contact else None,
            }
            data.append(item)
        return success_response(data=data, message="Tasks retrieved")

    except Exception as e:
        return internal_server_error(f"Failed to list tasks for user: {str(e)}")

async def update_task_for_user(db: AsyncSession, task_id: UUID, data: TaskUpdate):
    """Update a specific task for a user, focusing on status and callback_time."""
    try:
        if data.status is None:
            return error_response(400, "Status is required for update")
       
        task = await db.get(Task, task_id)
        if task is None:
            return error_response(404, "Task not found")
        
        # Keep both the pydantic model and a plain dict for downstream workflows
        task_model = TaskRead.model_validate(task)
        task_data = task_model.model_dump()

        # Now route based on status (use string lower for safe comparisons)
        status = data.status.strip().lower()
        if status == "interested":
            return await interested_func(
                db,
                action={
                    "models": {"task": task_data},
                    "data": {"remarks": data.remarks, "additional_data": data.additional_data},
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
        return internal_server_error(f"Failed to update task: {str(e)}")
