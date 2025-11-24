from app.utils.logging import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from fastapi import UploadFile, HTTPException
import os
import pandas as pd
import tempfile
from typing import Dict, Any, Optional, Tuple, Union
import datetime
from app.utils.dfs import load_kpi_config
from app.utils.context_vars import client_context
from pydantic import BaseModel
import json
import hashlib
from app.models.marketing_historic import MarketingEffectivenessHistorical, MarketingEffectivenessOptimiser

def get_unit_short(unit: str) -> dict:
    """
    Returns the unit_short object for the given unit from settings.UNIT_SHORT.
    Falls back to 'default' if unit is not found.
    """
    return settings.UNIT_SHORT.get(unit) or settings.UNIT_SHORT.get("default")

def get_client_from_context() -> str:
    """
    Get the client from the current context.
    This uses contextvars to retrieve the client set in the middleware.
    """
    return client_context.get()

def get_brand_unit():
    client = get_client_from_context()
    unit = settings.BRAND_CREATION.get(client).get('unit')
    return unit

def get_brand_iconName():
    unit = get_brand_unit()
    iconName = settings.UNIT_SHORT.get(unit).get('icon')
    return iconName

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


def get_days_short_options_from_timestamp(timestamp: int) -> dict:
    """
    Given a timestamp, calculate the difference in days from today,
    and return the DAYS_SHORTS options that are <= the diff,
    plus the next higher bucket (if any), and 'default'.

    Args:
        timestamp (int): Unix timestamp (seconds)

    Returns:
        dict: {key: label} for matching/lower ranges, next higher, and 'default'
    """
    input_date = datetime.datetime.fromtimestamp(timestamp).date()
    today = datetime.date.today()
    diff_days = (today - input_date).days

    # Collect numeric keys and sort
    numeric_keys = sorted(
        [int(k) for k in settings.DAYS_SHORTS.keys() if k != "default"]
    )

    result_keys = [k for k in numeric_keys if k <= diff_days]

    # Add the next higher bucket if it exists
    higher_keys = [k for k in numeric_keys if k > diff_days]
    if higher_keys:
        result_keys.append(higher_keys[0])

    # Build result dict
    result = {str(k): settings.DAYS_SHORTS[str(k)] for k in result_keys}
    result["default"] = settings.DAYS_SHORTS.get("default", "All Time")
    return result

def _format_currency(value: float, currency: str = None, isSymbol: bool = True) -> Dict[str, Any]:
    logger.info("Formatting currency", value=value, currency=currency)
    currency = get_brand_unit() if currency == None else currency
    unit_config = settings.UNIT_SHORT.get(currency, settings.UNIT_SHORT.get("default", {}))
    symbol = unit_config.get("symbol", "$")
    units = {k: v for k, v in unit_config.items() if k not in ["symbol", "icon"]}
    sorted_units = sorted(units.items(), key=lambda item: item[1], reverse=True)
    
    def process_number(x):
        x = round(x, 2)
        return int(x) if x == int(x) else x

    for unit_name, unit_value in sorted_units:
        if abs(value) >= unit_value:
            formatted_value = process_number(value / unit_value)
            result = {"pre": symbol if isSymbol else "", "value": formatted_value, "post": unit_name, "raw_value": value}
            logger.info("Currency formatting complete obj: Formatted currency details", eventObj={"Formatted currency details": result})
            return result
    
    formatted_value = process_number(value)
    result = {"pre": symbol if isSymbol else "", "value": formatted_value, "post": "", "raw_value": value}
    logger.info("Currency formatting complete obj: Formatted currency details", eventObj={"Formatted currency details": result})
    return result

def _format_percentage(value: float) -> Dict[str, Any]:
    logger.info("Formatting percentage", value=value)
    def process_number(x):
        return int(x) if x == int(x) else x
    
    formatted_value = process_number(round(value, 1))
    result = {"pre": "", "value": formatted_value, "post": "%", "raw_value": value}
    logger.info("Percentage formatting complete obj: Formatted percentage details", eventObj={"Formatted percentage details": result})
    return result

def _format_symbol(pre, value, post) -> Dict[str, Any]:
    return {"pre": pre, "value": value, "post": post, "raw_value": value}

def _format_no_unit(value: float) -> Dict[str, Any]:
    logger.info("Formatting number with no unit", value=value)
    def process_number(x):
        return int(x) if x == int(x) else x
    
    formatted_value = process_number(round(value, 1))
    result = {"pre": "", "value": formatted_value, "post": "", "raw_value": value}
    logger.info("Number formatting complete obj: Formatted number details", eventObj={"Formatted number details": result})
    return result

def _get_change_and_growth(current: Optional[float], previous: Optional[float]) -> Tuple[Optional[Union[str, float]], Optional[int]]:
    logger.info("Calculating change and growth", current=current, previous=previous)
    if current is None or previous is None:
        logger.warning("Cannot calculate change and growth with None values")
        return None, None
    if previous == 0:
        if current == 0:
            logger.info("Both current and previous are 0, returning 0.0 change and 0 growth")
            return "0.0", 0
        logger.warning("Cannot calculate change and growth with previous value as 0")
        return None, None

    change = ((current - previous) / previous) * 100
    growth = 1 if current > previous else -1 if current < previous else 0

    # Round the change to 1 decimal place for display
    rounded_change = round(change, 1)

    # Add explicit '+' sign for positive changes for clearer presentation
    if rounded_change > 0:
        signed_change: Union[str, float] = f"+{rounded_change}"
    else:
        signed_change = rounded_change

    result = signed_change, growth
    logger.info("Change and growth calculation complete obj: Calculated change and growth", eventObj={"Calculated change and growth": result})
    return result

async def detect_kpi_case_from_db(db: AsyncSession) -> str:
    """
    Implements the CASE logic:
    - CASE 1: if any row with type='business_kpi' and particular='sales'
    - CASE 2: if any row with type='business_kpi' and sub_type='brand_metric'
    - CASE 3: otherwise
    Returns: 'CASE 1', 'CASE 2', or 'CASE 3'
    """
    # Check for CASE 1
    case1_query = select(func.count()).select_from(MarketingEffectivenessHistorical).where(
        MarketingEffectivenessHistorical.year.isnot(None),
        MarketingEffectivenessHistorical.month.isnot(None),
        MarketingEffectivenessHistorical.type == 'business_kpi',
        MarketingEffectivenessHistorical.particular == 'sales'
    )
    result1 = await db.execute(case1_query)
    count1 = result1.scalar()
    if count1 > 0:
        return 'CASE 1'

    # Check for CASE 2
    case2_query = select(func.count()).select_from(MarketingEffectivenessHistorical).where(
        MarketingEffectivenessHistorical.year.isnot(None),
        MarketingEffectivenessHistorical.month.isnot(None),
        MarketingEffectivenessHistorical.type == 'business_kpi',
        MarketingEffectivenessHistorical.sub_type == 'brand_metric'
    )
    result2 = await db.execute(case2_query)
    count2 = result2.scalar()
    if count2 > 0:
        return 'CASE 2'

    # Default CASE 3
    return 'CASE 3'

async def fetch_tstp(db: AsyncSession, type:list = []) -> str:
    """
    fetches type, sub_type, particular from MarketingEffectivenessHistorical table and counts occurrences
    """
    query = select(
        MarketingEffectivenessHistorical.type,
        MarketingEffectivenessHistorical.sub_type,
        MarketingEffectivenessHistorical.particular,
        func.count().label('count')
    ).group_by(
        MarketingEffectivenessHistorical.type,
        MarketingEffectivenessHistorical.sub_type,
        MarketingEffectivenessHistorical.particular
    )

    if len(type) > 0:
        query = query.where(MarketingEffectivenessHistorical.type.in_(type))

    result = await db.execute(query)
    rows = result.fetchall()
    return [{"type": row.type, "sub_type": row.sub_type, "particular": row.particular, "count": row.count} for row in rows]

def get_kpi_config_based_tstp(tstp_data: list) -> dict:
    """
    Given a list of dicts with keys 'type', 'sub_type', 'particular', and 'count',
    returns a nested dict structure based on settings.KPI_CONFIG.
    """
    kpi_config = load_kpi_config()
    filtered = pd.DataFrame()  # Empty DataFrame to accumulate results

    for entry in tstp_data:
        type_ = entry['type']
        sub_type = entry['sub_type']
        particular = entry['particular']
        count = entry['count']

        filtered = filtered._append(kpi_config.where(
            (kpi_config.type == type_) &
            (kpi_config.sub_type == sub_type) &
            (kpi_config.particular == particular)
        ).dropna())

    return filtered

async def get_applicable_kpis(db: AsyncSession) -> pd.DataFrame:
    tstp = await fetch_tstp(db, ["business_kpi"])
    kpi_config = get_kpi_config_based_tstp(tstp)
    return kpi_config

async def fetch_tstp_all_records(db: AsyncSession, type: list = []) -> list:
    """
    Fetches all records from MarketingEffectivenessHistorical table, optionally filtered by type.
    Returns a list of dicts for each record (only column data, no SQLAlchemy internals).
    """
    query = select(MarketingEffectivenessHistorical)
    if len(type) > 0:
        query = query.where(MarketingEffectivenessHistorical.type.in_(type))
    result = await db.execute(query)
    rows = result.scalars().all()
    # Only return column data, not SQLAlchemy internals
    def row_to_dict(row):
        return {col.name: getattr(row, col.name) for col in row.__table__.columns}
    return [row_to_dict(row) for row in rows]

async def fetch_driver_impact_all_records(db: AsyncSession) -> list:
    """
    Fetches all records from MarketingEffectivenessOptimiser table, optionally filtered by type.
    Returns a list of dicts for each record (only column data, no SQLAlchemy internals).
    """
    query = select(MarketingEffectivenessOptimiser)
    result = await db.execute(query)
    rows = result.scalars().all()
    # Only return column data, not SQLAlchemy internals
    def row_to_dict(row):
        return {col.name: getattr(row, col.name) for col in row.__table__.columns}
    return [row_to_dict(row) for row in rows]

async def fetch_tstp_all_records_driver_contribution(db: AsyncSession, type: list = []) -> list:
    """
    Fetches all records from MarketingEffectivenessHistorical table, optionally filtered by type.
    Returns a list of dicts for each record (only column data, no SQLAlchemy internals).
    """
    query = select(
        MarketingEffectivenessHistorical.particular,
        MarketingEffectivenessHistorical.region,
        MarketingEffectivenessHistorical.brand,
        MarketingEffectivenessHistorical.value,
        MarketingEffectivenessHistorical.kpi
    ).where(MarketingEffectivenessHistorical.type == 'contribution')
    if len(type) > 0:
        query = query.where(MarketingEffectivenessHistorical.type.in_(type))
    result = await db.execute(query)
    rows = result.fetchall()
    return [
        {
            'particular': row.particular,
            'region': row.region,
            'brand': row.brand,
            'value': row.value,
            'kpi': row.kpi
        }
        for row in rows
    ]

def _format_summary_card(
    name: str,
    value_to_show: Dict = None,
    icon_name: str = "",
    value_in_num: Optional[int] = None,
    change_per: Optional[Union[str, int, float]] = None,
    growth: Optional[int] = None
) -> Dict:
    return {
        "name": name,
        "value_in_num": value_in_num,
        "value_to_show": value_to_show,
        "change_per": change_per,
        "growth": growth,
        "iconName": icon_name
    }

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