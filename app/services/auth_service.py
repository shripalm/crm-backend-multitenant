from typing import Optional
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.models.users import User
from app.core.security import verify_password, create_access_token, hash_password
from app.schemas.auth_schema import LoginRequest, LoginResponse, ForgotPasswordRequest
from app.core.config import settings
from app.utils.response import (
    success_response,
    error_response,
    internal_server_error,
)
from app.utils.logging import logger


async def authenticate_user(db: AsyncSession, login_data: LoginRequest) -> Optional[dict]:
    """
    Authenticate user with email/username and password.
    
    Args:
        db: Database session
        login_data: Login credentials (email_or_username, password)
        
    Returns:
        Success response with JWT token or error response
    """
    try:
        # Check if input is an email or username
        email_or_username = login_data.email_or_username.strip()
        
        # Query user by email or full_name (as username)
        # Case-insensitive search for better UX
        stmt = select(User).where(
            or_(
                func.lower(User.email) == func.lower(email_or_username),
                func.lower(User.full_name) == func.lower(email_or_username)
            )
        )
        
        result = await db.execute(stmt)
        # Use unique() to handle joined eager loads (roles relationship)
        user = result.unique().scalar_one_or_none()
        
        # User not found
        if not user:
            logger.warning(f"Login attempt failed - user not found: {email_or_username}")
            return error_response(
                status_code=401,
                message="Invalid email/username or password"
            )
        
        # Check if user is active
        if not user.active:
            logger.warning(f"Login attempt failed - user inactive: {user.email}")
            return error_response(
                status_code=403,
                message="Account is inactive. Please contact administrator."
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            logger.warning(f"Login attempt failed - invalid password for user: {user.email}")
            return error_response(
                status_code=401,
                message="Invalid email/username or password"
            )
        
        # Update last login time
        user.last_login = func.now()
        await db.commit()
        
        # Create JWT token
        token_data = {
            "user_id": user.id,
            "email": user.email
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Prepare response
        login_response = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return success_response(
            data=login_response.model_dump(),
            message="Login successful"
        )
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        await db.rollback()
        return internal_server_error(f"Authentication failed: {str(e)}")


async def verify_user_token(db: AsyncSession, user_id: str) -> Optional[User]:
    """
    Verify user exists and is active by user_id from token.
    
    Args:
        db: Database session
        user_id: User UUID from JWT token
        
    Returns:
        User object if valid and active, None otherwise
    """
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        # Use unique() to handle joined eager loads (roles relationship)
        user = result.unique().scalar_one_or_none()
        
        if user and user.active:
            return user
        return None
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return None


async def reset_password(db: AsyncSession, reset_data: ForgotPasswordRequest) -> Optional[dict]:
    """
    Reset user password (forgot password functionality).
    
    Args:
        db: Database session
        reset_data: Password reset data (email, new_password, confirm_password)
        
    Returns:
        Success response or error response
    """
    try:
        # Validate passwords match
        if reset_data.new_password != reset_data.confirm_password:
            return error_response(
                status_code=400,
                message="Passwords do not match"
            )
        
        # Find user by email
        stmt = select(User).where(func.lower(User.email) == func.lower(reset_data.email))
        result = await db.execute(stmt)
        user = result.unique().scalar_one_or_none()
        
        # User not found
        if not user:
            logger.warning(f"Password reset attempt for non-existent email: {reset_data.email}")
            return error_response(
                status_code=404,
                message="User with this email not found"
            )
        
        # Check if user is active
        if not user.active:
            logger.warning(f"Password reset attempt for inactive user: {user.email}")
            return error_response(
                status_code=403,
                message="Account is inactive. Please contact administrator."
            )
        
        # Update password
        user.password_hash = hash_password(reset_data.new_password)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Password reset successful for user: {user.email}")
        
        return success_response(
            data={
                "email": user.email,
                "message": "Password has been reset successfully"
            },
            message="Password reset successful"
        )
        
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}", exc_info=True)
        await db.rollback()
        return internal_server_error(f"Password reset failed: {str(e)}")

