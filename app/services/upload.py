from typing import List, Dict, Any
import pandas as pd
from io import BytesIO
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from app.models.contact import Contact

from app.utils.response import success_response, internal_server_error, error_response


async def process_file(db: AsyncSession, file_content: bytes, filename: str):
    """Process Excel or CSV file and return standardized response."""
    try:
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

        print(data)

        if data:
            # Filter out keys that are not actual Contact columns (protects against extra CSV headers)
            allowed_columns = set(['name', 'email', 'contact_no'])
            cleaned_records = [
                {
                    k: (str(v).strip() if v is not None else None)
                    for k, v in record.items()
                    if k in allowed_columns
                }
                for record in data
            ]

            if cleaned_records:
                stmt = insert(Contact).values(cleaned_records)
                await db.execute(stmt)
                await db.commit()

        return success_response(
            data=response_data, 
            message=f"File processed successfully. {rows_processed} rows imported."
        )
    
    except Exception as e:
        return internal_server_error(f"Failed to process file: {str(e)}")
