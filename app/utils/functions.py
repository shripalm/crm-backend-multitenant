from fastapi import UploadFile, HTTPException
import os
import pandas as pd
import tempfile
from typing import Dict, Any
from app.utils.context_vars import client_context
from pydantic import BaseModel
import json
import hashlib

def get_client_from_context() -> str:
    """
    Get the client from the current context.
    This uses contextvars to retrieve the client set in the middleware.
    """
    return client_context.get()

async def convert_to_json(file: UploadFile) -> Dict[str, Any]:
    """
    Convert uploaded Excel (xlsx) or CSV file to JSON format
    
    Args:
        file (UploadFile): Uploaded file (xlsx or csv)
        
    Returns:
        Dict[str, Any]: JSON compatible dictionary
        
    Raises:
        HTTPException: If file format is not supported or processing fails
    """
    # Check file extension
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    print(f"Received file: {file.filename} with extension: {file_extension}")  # Debug log
    
    if file_extension not in ['.xlsx', '.csv']:
        raise HTTPException(
            status_code=400,
            detail=f"Only .xlsx and .csv files are supported. Received file with extension: {file_extension}"
        )
    
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Write uploaded file content to temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Read file based on extension using pandas
            if file_extension == '.xlsx':
                df = pd.read_excel(temp_file.name)
            else:
                df = pd.read_csv(temp_file.name)
            
            # Convert DataFrame to JSON compatible dictionary
            json_data = df.to_dict(orient='records')
            
            return {
                "status": "200",
                "message": "Success",
                "data": json_data
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if 'temp_file' in locals():
            os.unlink(temp_file.name)

def sort_object(obj):
    """
    Recursively sorts dicts and lists, including Pydantic models.
    """
    print("--------------------------------")
    print(type(obj))

    # ✅ Convert Pydantic models to dicts first
    if isinstance(obj, BaseModel):
        obj = obj.model_dump()  # or obj.dict() for older Pydantic versions

    if isinstance(obj, dict):
        return {k: sort_object(v) for k, v in sorted(obj.items(), key=lambda x: x[0])}

    elif isinstance(obj, list):
        print("It's a list")
        obj = [sort_object(i) for i in obj]

        if all(isinstance(i, dict) and "NAME" in i for i in obj):
            print("All elements are dicts with NAME key")
            obj.sort(key=lambda x: str(x["NAME"]).lower())
        elif all(isinstance(i, str) for i in obj):
            obj.sort(key=lambda x: x.lower())

        return obj

    else:
        return obj

def object_to_sha(obj):
    """Convert any Python dict/list/object to a stable SHA256 hash."""
    from pydantic import BaseModel

    # Step 1: Convert Pydantic models to dicts
    if isinstance(obj, BaseModel):
        obj = obj.model_dump()

    # Step 2: Sort recursively (your function)
    sorted_obj = sort_object(obj)

    # Step 3: Convert to canonical JSON
    json_str = json.dumps(sorted_obj, ensure_ascii=False, separators=(",", ":"))

    # Step 4: Generate SHA256
    sha = hashlib.sha256(json_str.encode("utf-8")).hexdigest()

    return sha