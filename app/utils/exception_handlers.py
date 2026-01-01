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
    errors = {}
    
    for error in exc.errors():
        # Join all parts of the location for better context (e.g., "body.amount")
        loc_path = " -> ".join(str(l) for l in error["loc"])
        field_str = str(error["loc"][-1])
        error_type = error["type"].split(".")[-1]
        
        # Generate user-friendly error messages
        if error_type == "missing":
            msg = f"{field_str.replace('_', ' ').title()} is required"
        elif error_type == "string_type":
            msg = f"{field_str.replace('_', ' ').title()} must be a string"
        elif error_type in ["int_parsing", "float_parsing"]:
            msg = f"{field_str.replace('_', ' ').title()} must be a number"
        elif error_type == "enum":
            msg = f"Invalid value for {field_str.replace('_', ' ')}"
        else:
            msg = f"Validation error at {loc_path}: {error.get('msg', 'Invalid format')}"
            
        errors[loc_path] = msg
    
    error_response = ErrorResponse(
        status="422",
        message="Validation failed",
        data={
            "errors": errors
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
