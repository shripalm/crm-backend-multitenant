from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.task_table import Task
from app.models.users import User
from app.models.contact import Contact
from app.models.callreport import CallReport
from app.models.leads import Lead


async def _get_least_loaded_user_for_team(db: AsyncSession, team_keyword: str) -> Optional[User]:
    users_stmt = (
        select(User)
        .where(
            User.active.is_(True),
            User.team_name.ilike(team_keyword),
        )
        .order_by(User.id)
    )

    users_result = await db.execute(users_stmt)
    users = users_result.unique().scalars().all()

    if not users:
        return None

    user_ids = [user.id for user in users]
    task_counts = {}

    if user_ids:
        count_stmt = (
            select(Task.assigned_to, func.count(Task.id).label("task_count"))
            .where(Task.assigned_to.in_(user_ids))
            .group_by(Task.assigned_to)
        )
        count_result = await db.execute(count_stmt)
        task_counts = dict(count_result.all())

    user_task_counts = [
        (user, task_counts.get(user.id, 0))
        for user in users
    ]

    if not user_task_counts:
        return None

    user_task_counts.sort(key=lambda x: (x[1], str(x[0].id)))
    return user_task_counts[0][0]


async def assign_task_for_contact_presales(db: AsyncSession, contact: Contact) -> None:
    try:
        selected_user = await _get_least_loaded_user_for_team(db, "presales")
        if selected_user is None:
            return

        task = Task(
            lead_id=contact.id,
            assigned_to=selected_user.id,
            assigned_to_team="presales",
            status="pending",
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)
    except Exception as e:
        await db.rollback()
        print(f"Error in auto-assign (contact/presales): {str(e)}")


async def assign_task_for_call_report_sales(db: AsyncSession, call_report: CallReport) -> None:
    try:
        if not call_report.status or call_report.status.strip().lower() != "interested":
            return

        selected_user = await _get_least_loaded_user_for_team(db, "sales")
        if selected_user is None:
            return

        task = Task(
            lead_id=call_report.id,
            assigned_to=selected_user.id,
            assigned_to_team="sales",
            status="pending",
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)
    except Exception as e:
        await db.rollback()
        print(f"Error in auto-assign (call report/sales): {str(e)}")


async def assign_task_for_lead_site_visit(db: AsyncSession, lead: Lead) -> None:
    try:
        if not lead.site_visit:
            return

        selected_user = await _get_least_loaded_user_for_team(db, "sitevisit")
        if selected_user is None:
            return

        task = Task(
            lead_id=lead.id,
            assigned_to=selected_user.id,
            assigned_to_team="sitevisit",
            status="pending",
            remarks=lead.remark,
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)
    except Exception as e:
        await db.rollback()
        print(f"Error in auto-assign (lead/site visit): {str(e)}")
