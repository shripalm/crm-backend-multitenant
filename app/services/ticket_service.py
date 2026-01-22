from typing import Any, List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.ticket import Ticket
from app.models.agent import Agent
from app.models.users import User
from app.models.ticket_status_history import TicketStatusHistory
from app.models.ticket_comment import TicketComment
from app.schemas.ticket_schema import AgentTicketCreate, TicketRead
from app.utils.response import success_response, error_response, internal_server_error


async def create_agent_ticket(db: AsyncSession, data: AgentTicketCreate):
    """Create a ticket raised by an agent and return serialized response."""
    try:
        stmt = select(Agent).where(Agent.name == data.Agent_Name)
        result = await db.execute(stmt)
        agent = result.scalars().one_or_none()
        if agent is None:
            return error_response(404, "Agent not found")

        ticket = Ticket(
            category=data.Category,
            agent_id=agent.id,
            raised_by=agent.id,
            title=data.Title,
            description=data.Detailed_Description,
            priority=data.priority,
            status="OPEN",
            attachment_urls=data.Attachment,
        )

        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)

        # Log initial status entry
        history = TicketStatusHistory(
            ticket_id=ticket.id,
            old_status=None,
            new_status=ticket.status,
            changed_by_id=agent.id,
            changed_by_type="agent",
        )
        db.add(history)
        await db.commit()

        ticket_data = TicketRead.model_validate(ticket).model_dump()
        return success_response(data=ticket_data, message="Ticket created")

    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to create ticket: {str(e)}")


async def create_user_ticket(db: AsyncSession, current_user: User, data):
    """Create a ticket raised by an authenticated user and return serialized response."""
    try:
        ticket = Ticket(
            category=data.Category,
            agent_id=None,
            raised_by=current_user.id,
            title=data.Title,
            description=data.Detailed_Description,
            priority=data.priority,
            status="OPEN",
            attachment_urls=data.Attachment,
        )

        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)

        # Log initial status entry
        history = TicketStatusHistory(
            ticket_id=ticket.id,
            old_status=None,
            new_status=ticket.status,
            changed_by_id=current_user.id,
            changed_by_type="user",
        )
        db.add(history)
        await db.commit()

        ticket_data = TicketRead.model_validate(ticket).model_dump()
        return success_response(data=ticket_data, message="Ticket created")
    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to create ticket: {str(e)}")


async def list_agent_tickets(db: AsyncSession, user_db: Optional[AsyncSession] = None):
    """List tickets for agents and format fields as requested.

    Requirements:
    - Only include tickets where Category == "GENERAL".
    - Employee should always be resolved from Users (raised_by refers to a User).
    """
    try:
        stmt = select(Ticket).where(Ticket.category == "GENERAL")
        result = await db.execute(stmt)
        tickets: List[Ticket] = result.scalars().all()

        # Resolve employee names from default DB if provided
        employee_names: dict[Any, str] = {}
        user_ids = {t.raised_by for t in tickets if t.raised_by is not None}
        if user_ids and user_db is not None:
            user_stmt = select(User.id, User.full_name).where(User.id.in_(list(user_ids)))
            user_res = await user_db.execute(user_stmt)
            for uid, fullname in user_res.all():
                employee_names[uid] = fullname

        latest_map = await _latest_status_map(db, [t.id for t in tickets])
        data = []
        for t in tickets:
            emp_name = employee_names.get(t.raised_by, "-")
            old_new = latest_map.get(t.id)
            # Activity: first record should be 'Not Yet', else 'OLD -> NEW'
            if not old_new:
                activity = "Not Yet"
            else:
                old, new = old_new
                activity = "Not Yet" if not old else f"{old} -> {new}"
            item = {
                "Ticket_ID": f"TKT-{t.id}",
                "Employee": emp_name,
                "Category": t.category,
                "Priority": t.priority,
                "Title": t.title,
                "Description": t.description,
                "Submitted on": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(t.created_at, datetime) else str(t.created_at),
                "Status": t.status,
                "Activity": activity,
            }
            data.append(item)

        return success_response(data=data, message="Tickets retrieved")
    except Exception as e:
        return internal_server_error(f"Failed to list tickets: {str(e)}")


async def log_ticket_status_change(
    db: AsyncSession,
    *,
    ticket_id,
    old_status: str | None,
    new_status: str,
    changed_by_id=None,
    changed_by_type: str | None = None,
):
    try:
        entry = TicketStatusHistory(
            ticket_id=ticket_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_id=changed_by_id,
            changed_by_type=changed_by_type,
        )
        db.add(entry)
        await db.commit()
        return True
    except Exception:
        await db.rollback()
        return False


async def list_ticket_history(db: AsyncSession, ticket_id):
    try:
        stmt = select(TicketStatusHistory).where(TicketStatusHistory.ticket_id == ticket_id).order_by(TicketStatusHistory.created_at.asc())
        res = await db.execute(stmt)
        rows = res.scalars().all()
        from app.schemas.ticket_status_history_schema import TicketStatusHistoryRead
        data = [TicketStatusHistoryRead.model_validate(r).model_dump() for r in rows]
        return success_response(data=data, message="Ticket history retrieved")
    except Exception as e:
        return internal_server_error(f"Failed to fetch ticket history: {str(e)}")


async def update_ticket_status_and_comment(db: AsyncSession, ticket_id, data):
    try:
        ticket = await db.get(Ticket, ticket_id)
        if ticket is None:
            return error_response(404, "Ticket not found")

        old_status = ticket.status
        ticket.status = data.status
        await db.commit()
        await db.refresh(ticket)

        if data.comment:
            comment = TicketComment(
                ticket_id=ticket.id,
                user_id=data.user_id,
                user_role=data.user_role,
                comment=data.comment,
            )
            db.add(comment)
            await db.commit()

        await log_ticket_status_change(
            db,
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=data.status,
            changed_by_id=data.user_id,
            changed_by_type=("user" if data.user_role == "USER" else ("agent" if data.user_role == "AGENT" else "admin")),
        )

        updated = TicketRead.model_validate(ticket).model_dump()
        return success_response(data=updated, message="Ticket updated")
    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to update ticket: {str(e)}")


async def _latest_status_map(db: AsyncSession, ticket_ids: list):
    if not ticket_ids:
        return {}
    subq = (
        select(
            TicketStatusHistory.ticket_id.label("t_id"),
            func.max(TicketStatusHistory.created_at).label("max_created")
        )
        .where(TicketStatusHistory.ticket_id.in_(ticket_ids))
        .group_by(TicketStatusHistory.ticket_id)
        .subquery()
    )
    stmt = (
        select(TicketStatusHistory)
        .join(
            subq,
            (TicketStatusHistory.ticket_id == subq.c.t_id)
            & (TicketStatusHistory.created_at == subq.c.max_created)
        )
    )
    res = await db.execute(stmt)
    rows = res.scalars().all()
    return {r.ticket_id: (r.old_status, r.new_status) for r in rows}


async def list_admin_agent_panel_tickets(db: AsyncSession):
    """For super admin: tickets raised from Agent panel.

    Fields: Ticket_id, priority, Agent, Description, Status, Submitted_at
    Logic: raised_by is an Agent and/or agent_id is set. We will select tickets with agent_id not null and (raised_by in agents) if possible.
    """
    try:
        # Only tickets raised by an Agent (raised_by in Agent IDs)
        agent_ids_subq = select(Agent.id)
        stmt = (
            select(Ticket)
            .where(Ticket.raised_by.in_(agent_ids_subq))
            .where(Ticket.category == "SYSTEM")
        )
        result = await db.execute(stmt)
        tickets: List[Ticket] = result.scalars().all()

        # Fetch agent names for agent_id
        agent_ids = {t.agent_id for t in tickets if t.agent_id is not None}
        agent_names: dict[Any, str] = {}
        if agent_ids:
            agent_stmt = select(Agent).where(Agent.id.in_(list(agent_ids)))
            agent_res = await db.execute(agent_stmt)
            for ag in agent_res.scalars().all():
                agent_names[ag.id] = ag.name

        latest_map = await _latest_status_map(db, [t.id for t in tickets])
        data = []
        for t in tickets:
            agent_name = agent_names.get(t.agent_id, "-")
            old_new = latest_map.get(t.id)
            # Activity: first record should be 'Not Yet', else 'OLD -> NEW'
            if not old_new:
                activity = "Not Yet" 
            else:
                old, new = old_new
                activity = "Not Yet" if not old else f"{old} -> {new}"
            item = {
                "Ticket_id": f"TKT-{t.id}",
                "priority": t.priority,
                "Agent": agent_name,
                "Title": t.title,
                "Description": t.description or "",
                "Status": t.status,
                "Submitted_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(t.created_at, datetime) else str(t.created_at),
                "Activity": activity,
            }
            data.append(item)

        return success_response(data=data, message="Agent panel tickets retrieved")
    except Exception as e:
        return internal_server_error(f"Failed to list agent panel tickets: {str(e)}")


async def update_ticket_category(db: AsyncSession, ticket_id, new_category: str):
    """Update a ticket's category (e.g., GENERAL <-> SYSTEM)."""
    try:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = await db.execute(stmt)
        ticket: Ticket | None = result.scalars().one_or_none()
        if ticket is None:
            return error_response(404, "Ticket not found")

        ticket.category = new_category
        await db.commit()
        await db.refresh(ticket)

        payload = {
            "Ticket_id": f"TKT-{ticket.id}",
            "Category": ticket.category,
            "Status": ticket.status,
        }
        return success_response(data=payload, message="Ticket category updated")
    except Exception as e:
        await db.rollback()
        return internal_server_error(f"Failed to update ticket category: {str(e)}")


async def list_admin_user_panel_tickets(db: AsyncSession, user_db: Optional[AsyncSession] = None):
    """For super admin: tickets raised by Users.

    Fields: Ticket_id, priority, Agent, Employee_name, Description, Status, Submitted_at
    Logic: raised_by refers to a User id. Agent from ticket.agent_id (if any).
    """
    try:
        # Only tickets raised by Users (i.e., not Agents)
        agent_ids_subq = select(Agent.id)
        stmt = (
            select(Ticket)
            .where(Ticket.raised_by.notin_(agent_ids_subq))
            .where(Ticket.category == "SYSTEM")
        )
        result = await db.execute(stmt)
        tickets: List[Ticket] = result.scalars().all()

        # fetch agent names by agent_id
        agent_ids = {t.agent_id for t in tickets if t.agent_id is not None}
        agent_names: dict[Any, str] = {}
        if agent_ids:
            agent_stmt = select(Agent).where(Agent.id.in_(list(agent_ids)))
            agent_res = await db.execute(agent_stmt)
            for ag in agent_res.scalars().all():
                agent_names[ag.id] = ag.name

        # fetch employee/user names by raised_by from user_db (default DB)
        user_ids = {t.raised_by for t in tickets if t.raised_by is not None}
        user_names: dict[Any, str] = {}
        if user_ids and user_db is not None:
            user_stmt = select(User.id, User.full_name).where(User.id.in_(list(user_ids)))
            user_res = await user_db.execute(user_stmt)
            for uid, fullname in user_res.all():
                user_names[uid] = fullname

        latest_map = await _latest_status_map(db, [t.id for t in tickets])
        data = []
        for t in tickets:
            employee_name = user_names.get(t.raised_by, "-")
            agent_name = agent_names.get(t.agent_id, "-")
            old_new = latest_map.get(t.id)
            # Activity: first record should be 'Not Yet', else 'OLD -> NEW'
            if not old_new:
                activity = "Not Yet"
            else:
                old, new = old_new
                activity = "Not Yet" if not old else f"{old} -> {new}"
            item = {
                "Ticket_id": f"TKT-{t.id}",
                "priority": t.priority,
                "Agent": agent_name,
                "Employee_name": employee_name,
                "Title": t.title,
                "Description": t.description or "",
                "Status": t.status,
                "Submitted_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(t.created_at, datetime) else str(t.created_at),
                "Activity": activity,
            }
            data.append(item)

        return success_response(data=data, message="User panel tickets retrieved")
    except Exception as e:
        return internal_server_error(f"Failed to list user panel tickets: {str(e)}")
