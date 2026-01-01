
import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Add project root to path
sys.path.append("d:\\Backend\\CRM-Backend")

from app.api.v1.routers.payments import initiate_self_payment, paytm_callback
from app.schemas.payment_schema import InitiateSelfPaymentRequest
from app.enums.payment_enums import PaymentStatus, PaymentPlan
from app.models.users import User
from app.models.payment import Payment
from decimal import Decimal

async def test_initiate_self_payment():
    print("Testing initiate_self_payment...")
    
    # Mock Data
    mock_db = AsyncMock()
    mock_agent = User(id="12345678-1234-5678-1234-567812345678", email="test@agent.com")
    payload = InitiateSelfPaymentRequest(plan_code="PRO", duration_days=30)
    
    # Mock Service
    with patch("app.api.v1.routers.payments.paytm_service") as mock_service:
        mock_service.create_txn_token = AsyncMock(return_value={"raw_response": {}, "txn_token": "token123"})
        
        response = await initiate_self_payment(payload, mock_agent, mock_db)
        
        if response.amount == Decimal("2499.00"):
            print("✅ Amount Calculated Correctly: 2499.00")
        else:
            print(f"❌ Amount Mismatch: {response.amount}")
            
        if response.status == PaymentStatus.INITIATED:
            print("✅ Status is INITIATED")
        else:
            print(f"❌ Status fail: {response.status}")

async def test_paytm_callback_success():
    print("\nTesting paytm_callback (SUCCESS)...")
    
    # Mock Request
    mock_request = MagicMock()
    mock_request.form = AsyncMock(return_value={
        "ORDERID": "ORDER_123",
        "CHECKSUMHASH": "valid_checksum",
        "STATUS": "TXN_SUCCESS"
    })
    
    mock_db = AsyncMock()
    
    # Mock Existing Payment
    mock_payment = Payment(
        id="11111111-1111-1111-1111-111111111111",
        user_id="12345678-1234-5678-1234-567812345678",
        order_id="ORDER_123",
        amount=Decimal("2499.00"),
        status=PaymentStatus.INITIATED,
        payment_context={
            "plan_code": "PRO",
            "duration_days": 30,
            "purpose": "SUBSCRIPTION"
        }
    )
    
    # Mock DB Query Result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_payment
    mock_db.execute.return_value = mock_result
    
    with patch("app.api.v1.routers.payments.paytm_service") as mock_service:
        # Mock Signature Verification
        mock_service.verify_signature.return_value = True
        
        # Mock Server Verification
        mock_service.verify_payment_status = AsyncMock(return_value={
            "status": PaymentStatus.SUCCESS,
            "amount": "2499.00",
            "txn_id": "TXN_999",
            "raw_response": {}
        })
        
        response = await paytm_callback(mock_request, mock_db)
        
        if response["status"] == "SUCCESS":
            print("✅ Callback Processed Successfully")
        else:
            print(f"❌ Callback Failed: {response}")
            
        if mock_payment.status == PaymentStatus.SUCCESS:
            print("✅ Payment Record Updated to SUCCESS")
        else:
            print(f"❌ Payment Record Status: {mock_payment.status}")

async def main():
    await test_initiate_self_payment()
    await test_paytm_callback_success()

if __name__ == "__main__":
    asyncio.run(main())
