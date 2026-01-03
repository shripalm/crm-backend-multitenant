from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.billing_record import BillingRecord
from app.models.user_activity_log import UserActivityLog


@dataclass(frozen=True)
class BillingComputation:
    active_users: int
    price_per_user: Decimal
    total_amount: Decimal


def _month_start(d: date) -> date:
    return d.replace(day=1)


def _next_month_start(d: date) -> date:
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def get_price_per_user(active_user_count: int) -> Decimal:
    if active_user_count < 10:
        return Decimal("1399")
    if 10 <= active_user_count <= 15:
        return Decimal("1199")
    return Decimal("1000")


def compute_monthly_bill(active_user_count: int) -> BillingComputation:
    price = get_price_per_user(active_user_count)
    total = price * Decimal(active_user_count)
    return BillingComputation(active_users=active_user_count, price_per_user=price, total_amount=total)


async def count_active_users_for_agent(
    admin_db: AsyncSession,
    agent_id,
    billing_month: date,
) -> int:
    start = datetime.combine(_month_start(billing_month), datetime.min.time(), tzinfo=timezone.utc)
    end = datetime.combine(_next_month_start(_month_start(billing_month)), datetime.min.time(), tzinfo=timezone.utc)

    stmt = (
        select(func.count(func.distinct(UserActivityLog.user_id)))
        .where(
            and_(
                UserActivityLog.agent_id == agent_id,
                UserActivityLog.login_time >= start,
                UserActivityLog.login_time < end,
            )
        )
    )

    result = await admin_db.execute(stmt)
    value = result.scalar_one_or_none()
    return int(value or 0)


async def generate_billing_for_agent_month(
    admin_db: AsyncSession,
    agent_id,
    billing_month: date,
) -> BillingRecord:
    billing_month = _month_start(billing_month)

    existing_stmt = select(BillingRecord).where(
        and_(BillingRecord.agent_id == agent_id, BillingRecord.billing_month == billing_month)
    )
    existing = (await admin_db.execute(existing_stmt)).scalar_one_or_none()
    if existing is not None:
        return existing

    active_users = await count_active_users_for_agent(admin_db, agent_id, billing_month)
    computation = compute_monthly_bill(active_users)

    record = BillingRecord(
        agent_id=agent_id,
        billing_month=billing_month,
        active_users=computation.active_users,
        price_per_user=computation.price_per_user,
        total_amount=computation.total_amount,
        status="pending",
    )
    admin_db.add(record)
    await admin_db.commit()
    await admin_db.refresh(record)
    return record


async def generate_billing_for_all_agents_month(admin_db: AsyncSession, billing_month: date) -> list[BillingRecord]:
    billing_month = _month_start(billing_month)

    agents = (await admin_db.execute(select(Agent))).scalars().all()

    records: list[BillingRecord] = []
    for agent in agents:
        record = await generate_billing_for_agent_month(admin_db, agent.id, billing_month)
        records.append(record)

    return records
