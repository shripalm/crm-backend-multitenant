from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.response import StandardResponse
from app.services.visibility_service import get_user_visibility_metadata
from app.utils.logging import logger


router = APIRouter()


@router.get("/", response_model=StandardResponse[dict])
async def get_user_visibility(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get visibility metadata for the current authenticated user.

    Returns a dictionary mapping resource names to lists of allowed actions
    based on the user's roles and permissions.

    Example response:
    {
      "status": "200",
      "data": {
        "contacts": ["read", "create", "update"],
        "call_reports": ["read"]
      },
      "message": "User visibility retrieved successfully"
    }
    """
    try:
        visibility_data = await get_user_visibility_metadata(db, str(current_user.id))

        logger.info(
            f"Visibility retrieved for user {current_user.email}",
            user_id=str(current_user.id),
            resources_count=len(visibility_data)
        )

        return StandardResponse(
            status="200",
            message="User visibility retrieved successfully",
            data=visibility_data
        )

    except Exception as e:
        logger.error(f"Error retrieving visibility for user {current_user.email}: {str(e)}")
        return StandardResponse(
            status="500",
            message=f"Failed to retrieve user visibility: {str(e)}",
            data={}
        )

