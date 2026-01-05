from datetime import datetime, timedelta
import uuid
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.admin_session import get_admin_db
from app.api.deps import get_db, get_current_agent
from app.core.auth import get_current_user
from app.models.users import User
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.subscription import UserSubscription
from app.schemas.payment_schema import (
    InitiateAgentPaymentRequest,
    InitiateSelfPaymentRequest,
    PaymentInitiationResponse,
    SubscriptionStatusResponse,
    InvoiceRead
)
from app.enums.payment_enums import PaymentStatus, InvoiceStatus, PaymentPlan, PRICING_PLANS
from app.services.paytm_service import paytm_service
from app.utils.logging import logger

router = APIRouter()

# ==============================
# 1. ADMIN PAYMENT INITIATION
# ==============================

@router.post(
    "/agents/initiate", 
    response_model=PaymentInitiationResponse,
    summary="Initiate Agent Payment (ADMIN ONLY)",
    description="Requires a valid ADMIN JWT token. Agents are restricted from this endpoint (403)."
)
async def initiate_agent_payment(
    payload: InitiateAgentPaymentRequest,
    db: AsyncSession = Depends(get_admin_db),
    token: Optional[str] = Header(None, description="Admin Access Token")
):
    """
    Step 1 (Admin): Initiate a subscription payment for an agent.
    - **RESTRICTED**: Only accessible by Admin users.
    - Generates Paytm txn token for the target agent.
    - Returns 403 if called with an Agent token.
    - Returns 401 if token is missing or invalid.
    """
    # 1. AUTHENTICATION & ROLE CHECK
    if not token:
        raise HTTPException(
            status_code=401, 
            detail="Authentication required. Please provide an Admin token."
        )

    try:
        import jwt
        from app.core.config import settings
        token_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check for admin_id in token
        admin_id = token_payload.get("admin_id")
        user_id_agent = token_payload.get("user_id")

        if user_id_agent and not admin_id:
            # Token is valid but is an AGENT token
            logger.warning(f"Access denied: Agent {user_id_agent} tried to access Admin-only payment API")
            raise HTTPException(
                status_code=403, 
                detail="Access denied: This operation requires ADMIN privileges."
            )
            
        if not admin_id:
            logger.warning("Invalid token payload: missing admin_id")
            raise HTTPException(
                status_code=401, 
                detail="Invalid token. Please use a valid Admin JWT."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment initiation auth failure: {str(e)}")
        raise HTTPException(status_code=401, detail="Session expired or invalid token")

    # 2. Identify the target agent to be billed
    target_user_id = payload.target_agent_id

    # 3. Generate unique order ID
    order_id = f"ORDER_{uuid.uuid4().hex[:12]}".upper()
    
    # Create Payment Attempt (Locked Context for the target agent)
    payment = Payment(
        user_id=target_user_id,
        order_id=order_id,
        amount=payload.amount,
        status=PaymentStatus.INITIATED,
        payment_context={
            "plan_code": payload.plan_code,
            "duration_days": payload.duration_days,
            "purpose": "SUBSCRIPTION"
        }
    )
    
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    
    # Generate Paytm Token
    try:
        # Note: In a real environment, BASE_URL should be public
        callback_url = "http://localhost:8000/api/v1/payments/paytm/callback"
        paytm_response = await paytm_service.create_txn_token(
            order_id=order_id,
            amount=str(payload.amount),
            callback_url=callback_url
        )
        
        # Store metadata from gateway if needed
        payment.raw_response = paytm_response.get("raw_response")
        await db.commit()
        
        return PaymentInitiationResponse(
            order_id=order_id,
            status=PaymentStatus.INITIATED,
            amount=payload.amount
        )
        
    except Exception as e:
        logger.error(f"Paytm initiation failed: {str(e)}")
        payment.status = PaymentStatus.FAILED
        await db.commit()
        raise HTTPException(status_code=500, detail="Payment gateway unavailable")

# ==============================
# 2. AGENT SELF-PURCHASE (NEW)
# ==============================

@router.post(
    "/agents/self/initiate",
    response_model=PaymentInitiationResponse,
    summary="Agent Self-Purchase Subscription",
    description="Allows logged-in agents to purchase plans for themselves."
)
async def initiate_self_payment(
    payload: InitiateSelfPaymentRequest,
    current_agent: User = Depends(get_current_agent),
    db: AsyncSession = Depends(get_admin_db)
):
    """
    Step 1 (Agent): Initiate own subscription payment.
    - **AUTH**: Requires AGENT role (validated by dependency).
    - **AMOUNT**: Calculated on backend based on plan_code. Never trusted from frontend.
    """
    # 1. Validate Plan & Calculate Price
    try:
        plan_enum = PaymentPlan(payload.plan_code)
        amount = PRICING_PLANS.get(plan_enum)
        if not amount:
            raise ValueError("Price not configured for plan")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid plan code: {payload.plan_code}")

    # 2. Generate unique order ID
    order_id = f"ORDER_{uuid.uuid4().hex[:12]}".upper()

    # 3. Create Payment Record (INITIATED)
    payment = Payment(
        user_id=current_agent.id,
        order_id=order_id,
        amount=amount, # BACKEND CALCULATED
        status=PaymentStatus.INITIATED,
        payment_context={
            "plan_code": payload.plan_code,
            "duration_days": payload.duration_days,
            "purpose": "SUBSCRIPTION"
        }
    )

    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    # 4. Generate Paytm Token
    try:
        # Note: In a real environment, BASE_URL should be public
        callback_url = "http://localhost:8000/api/v1/payments/paytm/callback"
        paytm_response = await paytm_service.create_txn_token(
            order_id=order_id,
            amount=str(amount),
            callback_url=callback_url,
            customer_email=current_agent.email,
            customer_phone=current_agent.phone_number if hasattr(current_agent, 'phone_number') else None
        )

        payment.raw_response = paytm_response.get("raw_response")
        await db.commit()

        return PaymentInitiationResponse(
            order_id=order_id,
            status=PaymentStatus.INITIATED,
            amount=amount
        )

    except Exception as e:
        logger.error(f"Paytm initiation failed for agent {current_agent.id}: {str(e)}")
        payment.status = PaymentStatus.FAILED
        await db.commit()
        raise HTTPException(status_code=500, detail="Payment gateway initiation failed")


# ==============================
# 3. PAYTM CALLBACK (The Processor)
# ==============================

@router.post("/paytm/callback")
async def paytm_callback(request: Request, db: AsyncSession = Depends(get_admin_db)):
    """
    Step 2: Handle success/failure from Paytm.
    - Verifies Checksum (Critical).
    - Verifies Status with Paytm Server (Double Check).
    - Updates Payment & Activates Subscription.
    """
    # 1. Parse Data
    body = await request.form()
    params = dict(body)
    
    order_id = params.get("ORDERID")
    checksum = params.get("CHECKSUMHASH")

    if not order_id or not checksum:
        logger.error("Callback missing OrderID or Checksum")
        # Return 200 to acknowledge receipt even if invalid, to stop retries? 
        # Usually gateway expects 200. But we raise 400 for now.
        raise HTTPException(status_code=400, detail="Invalid callback parameters")

    # 2. Verify Signature
    is_valid = paytm_service.verify_signature(params, checksum)
    if not is_valid:
        logger.error(f"Checksum verification failed for order {order_id}")
        raise HTTPException(status_code=400, detail="Security check failed")

    # 3. Find Payment record
    stmt = select(Payment).where(Payment.order_id == order_id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()

    if not payment:
        logger.error(f"Callback received for unknown order {order_id}")
        raise HTTPException(status_code=404, detail="Order not found")

    # 4. Idempotency Check
    if payment.status == PaymentStatus.SUCCESS:
        return {"message": "Already processed", "status": "SUCCESS"}

    # 5. Verify Transaction Status with Paytm Server (Server-to-Server)
    try:
        verify_data = await paytm_service.verify_payment_status(order_id)
        gateway_status = verify_data.get("status") # PaymentStatus Enum
        gateway_amount = verify_data.get("amount")
        txn_id = verify_data.get("txn_id")
    except Exception as e:
        logger.error(f"Failed to verify status with Paytm: {e}")
        # Build logic: Could retry or trust callback if configured. 
        # Here we fail safe.
        raise HTTPException(status_code=502, detail="Failed to verify transaction with gateway")

    # 6. Process Result
    if gateway_status == PaymentStatus.SUCCESS:
        # Validate Amount (Prevent corruption)
        # Note: Gateway amount might be string, DB amount is Decimal
        if Decimal(gateway_amount) != payment.amount:
            logger.critical(f"Amount mismatch! Order: {payment.amount}, Paid: {gateway_amount}")
            payment.status = PaymentStatus.FAILED
            payment.raw_response = verify_data
            await db.commit()
            return {"status": "FAILED", "message": "Amount mismatch"}

        # A. Update Payment
        payment.status = PaymentStatus.SUCCESS
        payment.txn_id = txn_id
        payment.raw_response = verify_data
        
        # B. GENERATE INVOICE
        ctx = payment.payment_context
        year = datetime.now().year
        short_id = uuid.uuid4().hex[:6].upper()
        invoice_no = f"INV-{year}-{short_id}"
        
        invoice = Invoice(
            invoice_no=invoice_no,
            payment_id=payment.id,
            user_id=payment.user_id,
            amount=payment.amount,
            plan_code=ctx.get("plan_code"),
            purpose=ctx.get("purpose", "SUBSCRIPTION"),
            status=InvoiceStatus.PAID
        )
        db.add(invoice)
        
        # C. ACTIVATE SUBSCRIPTION
        sub_stmt = select(UserSubscription).where(UserSubscription.user_id == payment.user_id)
        sub_result = await db.execute(sub_stmt)
        sub = sub_result.scalar_one_or_none()
        
        try:
            duration = int(ctx.get("duration_days", 30))
        except:
            duration = 30
            
        expiry = datetime.now() + timedelta(days=duration)
        
        if sub:
            sub.plan_code = ctx.get("plan_code")
            sub.end_date = expiry
            sub.is_active = True
        else:
            sub = UserSubscription(
                user_id=payment.user_id,
                plan_code=ctx.get("plan_code"),
                end_date=expiry,
                is_active=True
            )
            db.add(sub)
            
        await db.commit()
        logger.info(f"Payment SUCCESS: Agent {payment.user_id} subscribed to {ctx.get('plan_code')}")
        return {"status": "SUCCESS", "invoice_no": invoice_no}

    else:
        # Handle Failure
        payment.status = PaymentStatus.FAILED
        payment.raw_response = verify_data
        await db.commit()
        logger.warning(f"Payment FAILED for order {order_id}")
        return {"status": "FAILED", "message": "Transaction failed at gateway"}


# ==============================
# 4. STATUS & INVOICE LOOKUP
# ==============================

@router.get("/subscriptions/status", response_model=SubscriptionStatusResponse)
async def get_sub_status(
    db: AsyncSession = Depends(get_admin_db),
    current_user: User = Depends(get_current_user)
):
    """Check current user's subscription status."""
    stmt = select(UserSubscription).where(UserSubscription.user_id == current_user.id)
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()
    
    if not sub or not sub.is_active:
        return SubscriptionStatusResponse(
            is_active=False,
            message="No active subscription found. Please pay to access features."
        )
        
    # Check if expired
    if sub.end_date < datetime.now():
        sub.is_active = False
        await db.commit()
        return SubscriptionStatusResponse(is_active=False, message="Subscription expired.")

    return SubscriptionStatusResponse(
        is_active=True,
        plan_code=sub.plan_code,
        expiry_date=sub.end_date,
        message="Active"
    )

@router.get("/invoices/my-latest", response_model=Optional[InvoiceRead])
async def get_latest_invoice(
    db: AsyncSession = Depends(get_admin_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest paid invoice for the current user."""
    stmt = select(Invoice).where(Invoice.user_id == current_user.id).order_by(Invoice.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().first()
