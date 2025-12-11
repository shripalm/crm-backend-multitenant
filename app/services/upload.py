from typing import List, Dict, Any
import pandas as pd
from io import BytesIO
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.contact import Contact
from app.services.contact_service import _auto_assign_task_for_contact
from app.utils.logging import logger

from app.utils.response import success_response, internal_server_error, error_response


async def process_file(db: AsyncSession, file_content: bytes, filename: str):
    """Process Excel or CSV file and return standardized response."""
    try:
        logger.info(f"Processing file: {filename}")
        file_lower = filename.lower()
        
        # Determine file type and read accordingly
        if file_lower.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(BytesIO(file_content))
            file_type = "excel"
        elif file_lower.endswith('.csv'):
            df = pd.read_csv(BytesIO(file_content))
            file_type = "csv"
        else:
            return error_response(400, "Invalid file type. Only .xlsx, .xls, and .csv files are allowed.")
            logger.error("Invalid file type. Only .xlsx, .xls, and .csv files are allowed.")
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict(orient='records')
        
        # Clean NaN values
        for record in data:
            for key, value in list(record.items()):
                if pd.isna(value):
                    record[key] = None
        
        rows_processed = len(data)
        
        response_data = {
            "filename": filename,
            "file_type": file_type,
            "rows_processed": rows_processed,
            "uploaded_at": datetime.now().isoformat(),
        }

        logger.debug(f"Data: {data}")

        success_count = 0
        if data:
            # Filter out keys that are not actual Contact columns (protects against extra CSV headers)
            allowed_columns = set(['name', 'email', 'contact_no', 'city', 'state', 'source', 
                                 'project_name', 'property_type', 'budget_range'])
            
            for record in data:
                try:
                    # Clean and validate the record
                    cleaned_record = {
                        k: (str(v).strip() if v is not None and not pd.isna(v) else None)
                        for k, v in record.items()
                        if k in allowed_columns
                    }
                    
                    # Skip if no valid data
                    if not any(cleaned_record.values()):
                        continue
                        
                    # Create contact one by one to trigger auto-assignment
                    contact = Contact(**cleaned_record)
                    db.add(contact)
                    await db.flush()  # Get the ID
                    
                    # Auto-assign task
                    await _auto_assign_task_for_contact(db, contact)
                    success_count += 1
                    
                except Exception as e:
                    await db.rollback()
                    print(f"Error processing record {record}: {str(e)}")
                    continue
                    
            await db.commit()

        return success_response(
            data={
                **response_data,
                "rows_successful": success_count,
                "rows_failed": rows_processed - success_count
            }, 
            message=f"File processed successfully. {success_count} of {rows_processed} rows imported."
        )
    
    except Exception as e:
        logger.error(f"Failed to process file: {str(e)}")
        return internal_server_error(f"Failed to process file: {str(e)}")
