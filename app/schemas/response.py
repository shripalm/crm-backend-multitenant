from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel

T = TypeVar('T')

class StandardResponse(BaseModel, Generic[T]):
    """
    Standard API response format for all endpoints
    """
    status: str
    message: str
    data: T = {}

    class Config:
        json_encoders = {
            # Add custom encoders if needed
        }

class ErrorResponse(BaseModel):
    """
    Standard error response format
    """
    status: str
    message: str
    data: Dict[str, Any] = {}

# Common success responses
class SuccessResponse(StandardResponse[T]):
    """
    Standard success response with data
    """
    status: str = "200"
    message: str = "Success"
    data: T = {}

class CreatedResponse(StandardResponse[T]):
    """
    Standard created response
    """
    status: str = "201"
    message: str = "Success"
    data: T = {}

class NoContentResponse(StandardResponse[None]):
    """
    Standard no content response for delete operations
    """
    status: str = "204"
    message: str = "Success"
    data: dict = {}
