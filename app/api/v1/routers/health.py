from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_engine

from app.db.session import get_db
from app.schemas.response import StandardResponse
from app.utils.response import success_response, internal_server_error

router = APIRouter()

@router.get("/health", response_model=StandardResponse[dict])
async def health_check():
    """Basic health check endpoint"""
    return success_response({"status": "healthy"}, "Service is healthy")

@router.get("/health/db", response_model=StandardResponse[dict])
async def database_health_check(request: Request, db: AsyncSession = Depends(get_db)):
    """Check database connectivity and pool status"""
    try:
        # Test connectivity
        await db.execute(text("SELECT 1"))

        # Always pull from the default async_engine
        pool_info = {}
        if async_engine and async_engine.pool:
            pool_info = {
                "pool_size": async_engine.pool.size(),
                "checked_in": async_engine.pool.checkedin(),
                "checked_out": async_engine.pool.checkedout(),
                "overflow": async_engine.pool.overflow(),
                "total_connections": async_engine.pool.size() + async_engine.pool.overflow(),
            }

        health_data = {
            "status": "healthy",
            "database": "connected",
            "client": request.headers.get("client", "unknown"),
            "pool_info": pool_info,
        }

        return success_response(health_data, "Database is healthy")

    except Exception as e:
        raise internal_server_error(f"Database unhealthy: {str(e)}")