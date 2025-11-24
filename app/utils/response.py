from typing import Any, Optional, Dict
from fastapi import HTTPException
from app.schemas.response import (
    StandardResponse, 
    ErrorResponse, 
    SuccessResponse, 
    CreatedResponse, 
    NoContentResponse
)

def success_response(data: Any, message: str = "Success") -> StandardResponse:
    """
    Create a standardized success response
    """
    return SuccessResponse(
        status="200",
        message=message,
        data=data
    )

def created_response(data: Any, message: str = "Success") -> StandardResponse:
    """
    Create a standardized created response
    """
    return CreatedResponse(
        status="201", 
        message=message,
        data=data
    )

def no_content_response(message: str = "Success") -> StandardResponse:
    """
    Create a standardized no content response for delete operations
    """
    return NoContentResponse(
        status="204",
        message=message,
        data=None
    )

def error_response(
    status_code: int, 
    message: str, 
    detail: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Create a standardized error response
    Raises HTTPException with the standardized format
    """
    error_data = ErrorResponse(
        status=str(status_code),
        message=detail or message,
        data=data or {}
    )
    
    raise HTTPException(
        status_code=status_code,
        detail=error_data.model_dump()
    )

# Common error responses
def not_found_error(message: str = "Resource not found") -> HTTPException:
    """
    Standard 404 error response
    """
    return error_response(404, message)

def bad_request_error(message: str = "Bad request") -> HTTPException:
    """
    Standard 400 error response
    """
    return error_response(400, message)

def internal_server_error(message: str = "Internal server error") -> HTTPException:
    """
    Standard 500 error response
    """
    return error_response(500, message)

def validation_error(message: str = "Validation failed", data: Optional[Dict[str, Any]] = None, status_code: int = 422) -> HTTPException:
    """
    Standard 422 | Status Code validation error response
    """
    return error_response(status_code=status_code, message = message, data=data)
