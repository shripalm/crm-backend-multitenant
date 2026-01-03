
import asyncio
import sys
import os
import jwt
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

# Add project root to path
sys.path.append("d:\\Backend\\CRM-Backend")

from app.core.auth import get_current_user
from app.core.config import settings

async def test_auth_extraction():
    print("Testing JWT extraction and verification...")
    
    SECRET_KEY = settings.SECRET_KEY
    user_id = "12345678-1234-5678-1234-567812345678"
    
    # Generate Token with aud/iss to test loosening
    token_data = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "aud": "some-audience",
        "iss": "some-issuer"
    }
    encoded_token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    
    # Mock DB
    mock_db = AsyncMock()
    
    # Case 1: Raw JWT in 'token' header
    print("  Testing raw token...")
    try:
        # We need to mock User query as it will fail on actual DB
        with patch("app.core.auth.select") as mock_select:
            mock_result = MagicMock()
            mock_user = MagicMock()
            mock_user.email = "test@example.com"
            mock_result.scalars().first.return_value = mock_user
            mock_db.execute.return_value = mock_result
            
            user = await get_current_user(token=encoded_token, db=mock_db)
            print("  ✅ Raw token accepted (aud/iss ignored)")
    except Exception as e:
        print(f"  ❌ Raw token failed: {e}")

    # Case 2: Bearer JWT in 'token' header
    print("  Testing Bearer token...")
    try:
        bearer_token = f"Bearer {encoded_token}"
        with patch("app.core.auth.select") as mock_select:
            mock_result = MagicMock()
            mock_user = MagicMock()
            mock_user.email = "test@example.com"
            mock_result.scalars().first.return_value = mock_user
            mock_db.execute.return_value = mock_result
            
            user = await get_current_user(token=bearer_token, db=mock_db)
            print("  ✅ Bearer token accepted")
    except Exception as e:
        print(f"  ❌ Bearer token failed: {e}")

async def main():
    await test_auth_extraction()

if __name__ == "__main__":
    asyncio.run(main())
