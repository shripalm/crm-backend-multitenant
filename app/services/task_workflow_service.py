from app.models.contact import Contact
from app.models.callreport import CallReport
from app.models.leads import Lead
from app.models.sitevisit import SiteVisit
from app.models.task_table import Task

from app.utils.response import success_response, error_response, internal_server_error

from sqlalchemy.ext.asyncio import AsyncSession

async def interested_func(db: AsyncSession, action: object) -> bool:
    try:
        return success_response(data=action["models"]["task"], message="Marked as Interested")
    except Exception as e:
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
        return success_response(data={"id": task_id}, message="Marked for Callback")
    except Exception as e:
        return internal_server_error(f"Failed to update task: {str(e)}")

async def lead_drop_func(db: AsyncSession, action: object) -> bool: # not interested
    try:
        task_id = action["models"]["task"]["id"]
        task = await db.get(Task, task_id)
        if task is None:
            return error_response(404, "Task not found")
        task.status = "not interested"
        task.remarks = action["data"]["remarks"] or task.remarks
        await db.commit()
        await db.refresh(task)
        return success_response(data={"id": task_id}, message="Marked as Not Interested")
    except Exception as e:
        return internal_server_error(f"Failed to update task: {str(e)}")
    

crm_data_leads_wf_definition = {
    "raw": {
        "table": Contact,
        "next_stage": "presales",
    },
    "presales": {
        "table": CallReport,
        "next_stage": "sales",
    },
    "sales": {
        "table": Lead,
        "next_stage": "sitevisit",
    },
    "sitevisit": {
        "table": SiteVisit,
        "next_stage": None,
    },
}