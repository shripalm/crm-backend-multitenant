from app.models.contact import Contact
from app.models.callreport import CallReport
from app.models.leads import Lead
from app.models.sitevisit import SiteVisit
from app.models.task_table import Task

from app.utils.response import success_response, error_response, internal_server_error
from app.utils.logging import logger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func


async def interested_func(db: AsyncSession, action: dict):
    """Workflow for marking a task/lead as Interested.

    Expects `action` to contain:
    - models.task: serialized task dict (including id and optional lead_id/contact_id)
    - data.remarks: optional updated remarks
    """
    try:
        task_id = action["models"]["task"]["id"]
        logger.info("Processing interested workflow", task_id=str(task_id))
        task = await db.get(Task, task_id)
        if task is None:
            logger.warning("Task not found for interested workflow", task_id=str(task_id))
            return error_response(404, "Task not found")

        # Update task status and remarks
        task.status = "interested"
        _data = action.get("data", {}).get("additional_data", {})
        remarks = action.get("data", {}).get("remarks")
        if remarks is not None:
            task.remarks = remarks or task.remarks

        # Treat lead_id as contact reference and log activity
        current_lead_id = action["models"]["task"].get("lead_id")
        current_team = action["models"]["task"].get("assigned_to_team") or "raw"
        prev_stage = crm_data_leads_wf_definition.get(current_team, {}).get("prev_stage")
        current_table = crm_data_leads_wf_definition.get(prev_stage, {}).get("table")
        logger.debug(
            "Interested workflow contact lookup",
            task_id=str(task_id),
            contact_id=str(current_lead_id) if current_lead_id else None,
        )
        print(current_team, current_table)
        if current_lead_id is not None:
            lead_data = await db.get(current_table, current_lead_id)
            if lead_data is not None:
                next_stage = crm_data_leads_wf_definition.get(prev_stage, {}).get("next_stage")
                next_table = crm_data_leads_wf_definition.get(next_stage, {}).get("table")
                print(next_stage, next_table)
                activity = next_table(
                    # common fields: employee_id, remark, created_at, contact_id
                    # constants
                    created_at=func.now(),
                    # from task table
                    employee_id=getattr(task, "assigned_to", None),
                    # from current table
                    contact_id=lead_data.id,
                    # from data
                    remark=f"Lead marked as Interested - {remarks}" if remarks else "Lead marked as Interested",
                    **(_data or {})
                )
                db.add(activity)
                logger.info("Logged interested activity", contact_id=str(activity.id), task_id=str(task_id))

        await db.commit()
        await db.refresh(task)
        logger.info("Task marked as interested", task_id=str(task_id))
        return success_response(data={"id": task_id}, message="Marked as Interested")
    except Exception as e:
        logger.error(f"Failed interested workflow for task {task_id}: {str(e)}")
        return internal_server_error(f"Failed to update task: {str(e)}")


async def callback_func(db: AsyncSession, action: object) -> bool:
    try:
        task_id = action["models"]["task"]["id"]
        task = await db.get(Task, task_id)
        if task is None:
            return error_response(404, "Task not found")
        task.status = "callback"
        task.callback_time = action["data"]["callback_time"]
        task.remarks = action["data"]["remarks"] or task.remarks
        await db.commit()
        await db.refresh(task)
        logger.info("Task marked for callback", task_id=str(task_id))
        return success_response(data={"id": task_id}, message="Marked for Callback")
    except Exception as e:
        logger.error(f"Failed callback workflow for task {task_id}: {str(e)}")
        return internal_server_error(f"Failed to update task: {str(e)}")


async def lead_drop_func(db: AsyncSession, action: object) -> bool:  # not interested
    try:
        task_id = action["models"]["task"]["id"]
        task = await db.get(Task, task_id)
        if task is None:
            return error_response(404, "Task not found")
        task.status = "not interested"
        task.remarks = action["data"]["remarks"] or task.remarks
        await db.commit()
        await db.refresh(task)
        logger.info("Task marked as not interested", task_id=str(task_id))
        return success_response(data={"id": task_id}, message="Marked as Not Interested")
    except Exception as e:
        logger.error(f"Failed not interested workflow for task {task_id}: {str(e)}")
        return internal_server_error(f"Failed to update task: {str(e)}")


crm_data_leads_wf_definition = {
    "raw": {
        "table": Contact,
        "next_stage": "presales",
        "prev_stage": None,
    },
    "presales": {
        "table": CallReport,
        "next_stage": "sales",
        "prev_stage": "raw",
    },
    "sales": {
        "table": Lead,
        "next_stage": "sitevisit",
        "prev_stage": "presales",
    },
    "sitevisit": {
        "table": SiteVisit,
        "next_stage": None,
        "prev_stage": "sales",
    },
}