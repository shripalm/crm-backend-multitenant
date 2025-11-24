from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.schemas.response import ErrorResponse
from app.utils.logging import logger

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTPException and return standardized error response
    """
    # Check if the detail is already in our standard format
    if isinstance(exc.detail, dict) and "status" in exc.detail:
        # Already formatted, return as is
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    # Format as standard error response
    error_response = ErrorResponse(
        status=str(exc.status_code),
        message=str(exc.detail) if exc.detail else "An error occurred",
        data={}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation errors and return standardized error response
    """
    error_response = ErrorResponse(
        status="422",
        message="Validation failed",
        data={
            "validation_errors": exc.errors(),
            "body": str(exc.body) if hasattr(exc, 'body') else None
        }
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions and return standardized error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = ErrorResponse(
        status="500",
        message="Internal server error",
        data={}
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )
