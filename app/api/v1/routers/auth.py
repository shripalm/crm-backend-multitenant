from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.schemas.auth_schema import LoginRequest, LoginResponse, ForgotPasswordRequest
from app.schemas.response import StandardResponse
from app.services.auth_service import authenticate_user, verify_user_token, reset_password
from app.core.security import verify_token
from app.utils.logging import logger

router = APIRouter()
# security = HTTPBearer()


@router.post("/login", response_model=StandardResponse[LoginResponse])
async def login(
    login_data: LoginRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    User login endpoint.
    
    Accepts either email or username along with password.
    Returns JWT access token on successful authentication.
    
    - **email_or_username**: User's email address or username
    - **password**: User's password (minimum 6 characters)
    
    Returns:
    - **access_token**: JWT token for subsequent authenticated requests
    - **token_type**: Always "bearer"
    - **user_id**: UUID of the authenticated user
    - **email**: Email of the authenticated user
    - **full_name**: Full name of the authenticated user
    - **expires_in**: Token expiration time in minutes
    """
    return await authenticate_user(db, login_data)


@router.post("/forgot-password", response_model=StandardResponse)
async def forgot_password(
    reset_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Forgot password endpoint.
    
    Allows users to reset their password by providing:
    - Email address
    - New password
    - Confirm password
    
    The passwords must match and meet minimum requirements.
    
    - **email**: User's email address
    - **new_password**: New password (minimum 6 characters)
    - **confirm_password**: Confirm new password (must match new_password)
    
    Returns:
    - Success message if password reset is successful
    - Error message if user not found, passwords don't match, or account is inactive
    """
    return await reset_password(db, reset_data)


# @router.get("/verify-token")
# async def verify_user_access_token(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Verify JWT token validity.
    
#     Requires Authorization header with Bearer token.
#     Returns user information if token is valid.
    
#     Headers:
#     - **Authorization**: Bearer {your_jwt_token}
#     """
#     token = credentials.credentials
    
#     # Verify and decode token
#     payload = verify_token(token)
#     if not payload:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Get user_id from payload
#     user_id = payload.get("user_id")
#     if not user_id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token payload",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Verify user exists and is active
#     user = await verify_user_token(db, user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found or inactive",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     return {
#         "valid": True,
#         "user_id": str(user.id),
#         "email": user.email,
#         "full_name": user.full_name,
#         "message": "Token is valid"
#     }


# @router.post("/logout")
# async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     """
#     User logout endpoint.
    
#     Note: JWT tokens are stateless, so logout is handled client-side
#     by removing the token. This endpoint serves as a placeholder for
#     future enhancements (e.g., token blacklisting).
    
#     Headers:
#     - **Authorization**: Bearer {your_jwt_token}
#     """
#     logger.info("User logout requested")
#     return {
#         "message": "Logout successful. Please remove the token from client.",
#         "success": True
#     }
