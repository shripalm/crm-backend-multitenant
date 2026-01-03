from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.admin_session import get_admin_db
from app.schemas.billing_schema import BillingRecordRead
from app.services.billing_service import generate_billing_for_all_agents_month
from app.models.billing_record import BillingRecord
from app.models.agent import Agent
from app.utils.logging import logger

router = APIRouter()


@router.post(
    "/generate",
    response_model=list[BillingRecordRead],
    status_code=status.HTTP_201_CREATED,
    summary="Generate monthly billing records",
    description="Generate billing records for all agents for the specified month. "
                "If no month is provided, uses the previous month."
)
async def generate_billing(
    month: Optional[date] = Query(
        None,
        description="Billing month in YYYY-MM format. Defaults to previous month.",
        example="2025-12-01"
    ),
    admin_db: AsyncSession = Depends(get_admin_db)
):
    """
    Generate monthly billing records for all agents.
    
    If no month is provided, it will use the first day of the previous month.
    """
    try:
        # If no month provided, default to first day of previous month
        if month is None:
            today = date.today()
            if today.month == 1:
                month = date(today.year - 1, 12, 1)
            else:
                month = date(today.year, today.month - 1, 1)
        else:
            # Ensure we use the first day of the month
            month = month.replace(day=1)
        
        logger.info(f"Admin triggered billing generation for {month.strftime('%B %Y')}")
        
        # Generate billing records
        records = await generate_billing_for_all_agents_month(
            admin_db=admin_db,
            billing_month=month
        )
        
        # Add agent names to the response
        records_with_agent_names = []
        total_amount = 0
        
        for record in records:
            # Get the agent's name
            agent = await admin_db.get(Agent, record.agent_id)
            
            # Create a dictionary with all required fields
            record_data = {
                'id': record.id,
                'agent_id': record.agent_id,
                'agent_name': agent.name if agent else "Unknown",
                'billing_month': record.billing_month,
                'active_users': record.active_users,
                'price_per_user': float(record.price_per_user),
                'total_amount': float(record.total_amount),
                'status': record.status,
                'created_at': record.created_at
            }
            
            # Validate with the schema
            record_dict = BillingRecordRead(**record_data).model_dump(mode='json')
            records_with_agent_names.append(record_dict)
            total_amount += record.total_amount
        
        # Add custom headers with summary information
        headers = {
            "X-Billing-Records-Count": str(len(records)),
            "X-Billing-Total-Amount": f"{total_amount:.2f}",
            "X-Billing-Currency": "INR"
        }
        
        logger.info(
            f"Generated {len(records)} billing records for {month.strftime('%B %Y')} "
            f"with total amount ₹{total_amount:,.2f}"
        )
        
        return JSONResponse(
            content=records_with_agent_names,
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"Error generating billing records: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate billing records"
        )


@router.post(
    "/regenerate",
    response_model=list[BillingRecordRead],
    status_code=status.HTTP_201_CREATED,
    summary="Force regenerate monthly billing records",
    description="Delete existing billing records and regenerate them for the specified month. "
                "This will recalculate based on all user logins including new ones."
)
async def regenerate_billing(
    month: Optional[date] = Query(
        None,
        description="Billing month in YYYY-MM format. Defaults to previous month.",
        example="2025-12-01"
    ),
    admin_db: AsyncSession = Depends(get_admin_db)
):
    """
    Force regenerate monthly billing records for all agents.
    This deletes existing records and creates new ones.
    """
    try:
        # If no month provided, default to first day of previous month
        if month is None:
            today = date.today()
            if today.month == 1:
                month = date(today.year - 1, 12, 1)
            else:
                month = date(today.year, today.month - 1, 1)
        else:
            # Ensure we use the first day of the month
            month = month.replace(day=1)
        
        logger.info(f"Force regenerating billing records for {month.strftime('%B %Y')}")
        
        # Delete existing billing records for this month
        from sqlalchemy import delete
        delete_stmt = delete(BillingRecord).where(BillingRecord.billing_month == month)
        result = await admin_db.execute(delete_stmt)
        deleted_count = result.rowcount
        await admin_db.commit()
        
        logger.info(f"Deleted {deleted_count} existing billing records")
        
        # Generate new billing records
        records = await generate_billing_for_all_agents_month(
            admin_db=admin_db,
            billing_month=month
        )
        
        # Add agent names to the response
        records_with_agent_names = []
        total_amount = 0
        
        for record in records:
            # Get the agent's name
            agent = await admin_db.get(Agent, record.agent_id)
            
            # Create a dictionary with all required fields
            record_data = {
                'id': record.id,
                'agent_id': record.agent_id,
                'agent_name': agent.name if agent else "Unknown",
                'billing_month': record.billing_month,
                'active_users': record.active_users,
                'price_per_user': float(record.price_per_user),
                'total_amount': float(record.total_amount),
                'status': record.status,
                'created_at': record.created_at
            }
            
            # Validate with the schema
            record_dict = BillingRecordRead(**record_data).model_dump(mode='json')
            records_with_agent_names.append(record_dict)
            total_amount += record.total_amount
        
        # Add custom headers with summary information
        headers = {
            "X-Billing-Records-Count": str(len(records)),
            "X-Billing-Total-Amount": f"{total_amount:.2f}",
            "X-Billing-Currency": "INR",
            "X-Billing-Deleted-Count": str(deleted_count)
        }
        
        logger.info(
            f"Regenerated {len(records)} billing records for {month.strftime('%B %Y')} "
            f"with total amount ₹{total_amount:,.2f} (deleted {deleted_count} old records)"
        )
        
        return JSONResponse(
            content=records_with_agent_names,
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"Error regenerating billing records: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate billing records"
        )
