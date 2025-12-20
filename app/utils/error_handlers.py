from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Dict, Any

def get_field_error_message(field: str, error_type: str) -> str:
    """Returns user-friendly error messages based on field and error type"""
    error_messages = {
        "missing": f"{field.replace('_', ' ').title()} is required",
        "string_type": f"{field.replace('_', ' ').title()} must be a string",
        "number_type": f"{field.replace('_', ' ').title()} must be a number",
        "invalid_format": f"Invalid format for {field.replace('_', ' ')}",
        "value_error": f"Invalid value for {field.replace('_', ' ')}"
    }
    return error_messages.get(error_type, f"Validation error for {field}")

def process_validation_error(exc: RequestValidationError) -> Dict[str, Any]:
    """Process validation errors and format them"""
    errors = {}
    
    for error in exc.errors():
        field = error["loc"][-1]  # Get the field name
        error_type = error["type"].split(".")[-1]  # Get the error type
        
        if error_type == "missing":
            msg = get_field_error_message(str(field), "missing")
        elif error_type == "string_type":
            msg = get_field_error_message(str(field), "string_type")
        elif error_type in ["int_parsing", "float_parsing"]:
            msg = get_field_error_message(str(field), "number_type")
        else:
            msg = get_field_error_message(str(field), "value_error")
            
        errors[str(field)] = msg
    
    return errors

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Global handler for request validation errors"""
    errors = process_validation_error(exc)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "422",
            "message": "Validation failed",
            "data": {
                "errors": errors
            }
        }
    )
