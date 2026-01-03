#!/usr/bin/env python3
"""
CLI script to generate monthly billing records for all agents.

Usage:
    python -m scripts.generate_billing [--month YYYY-MM]
    
If --month is not provided, it will use the first day of the previous month.
"""
import asyncio
import argparse
from datetime import datetime, date, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.base import engine as default_engine
from app.db.admin_session import engine as admin_engine
from app.services.billing_service import generate_billing_for_all_agents_month
from app.core.logging_config import setup_logging

logger = setup_logging()


def parse_args():
    parser = argparse.ArgumentParser(description="Generate monthly billing records for all agents.")
    parser.add_argument(
        "--month",
        type=str,
        help="Billing month in YYYY-MM format (e.g., 2025-12)",
    )
    return parser.parse_args()


def parse_month(month_str: Optional[str]) -> date:
    if month_str:
        return datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
    
    # Default to first day of previous month
    today = date.today()
    if today.month == 1:
        return date(today.year - 1, 12, 1)
    return date(today.year, today.month - 1, 1)


async def main():
    args = parse_args()
    billing_month = parse_month(args.month)
    
    logger.info(f"Generating billing records for {billing_month.strftime('%B %Y')}")
    
    # We only need the admin DB connection for this script
    async with admin_engine.begin() as conn:
        # Create async session factory
        async_session = async_sessionmaker(admin_engine, expire_on_commit=False)
        
        try:
            # Generate billing for all agents
            records = await generate_billing_for_all_agents_month(
                admin_db=async_session(),
                billing_month=billing_month
            )
            
            logger.info(f"Successfully generated {len(records)} billing records")
            
            # Log summary
            total_amount = sum(record.total_amount for record in records)
            logger.info(f"Total billing amount for {billing_month.strftime('%B %Y')}: ₹{total_amount:,.2f}")
            
        except Exception as e:
            logger.error(f"Error generating billing records: {str(e)}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(main())
