from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import make_url
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.models.users import User
from app.db.session import get_db
from app.core.security import verify_token
from app.utils.logging import logger
from app.utils.context_vars import client_context
from app.core.config import settings
from app.schemas.response import ErrorResponse



class ClientHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware that validates a `client` header and provides a per-request DB session.

    Behavior:
    - Requires header `client` to be one of the allowed keys (godrej, meesho).
    - Builds a DB URL by replacing the database name in `settings.DB_URLS['default']` with the mapped DB.
    - Creates an async engine and sessionmaker and stores them on `request.state`:
        - request.state.async_engine
        - request.state.async_session (callable sessionmaker)
        - request.state.client
    - Disposes the engine after the response completes.
    - Skips validation for certain paths (like metadata endpoints).
    """

    # mapping is now provided by settings; app.state will cache per-client engines

    # Paths that should skip client header validation
    SKIP_PATHS = [
        "/docs",
        "/openapi.json",
        "/api/v1/health",
        "/api/settings/db_migrate",
        "/api/settings/db_downgrade",
        "/api/settings/brand_creation",
        "/api/settings/db_version_check",
        "/api/settings/db_drop_all",
    ]

    def _add_cors_headers(self, response: Response, request: Request):
        """Add CORS headers to the response."""
        origin = request.headers.get("origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"

        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"

        # Handle preflight requests
        if request.method == "OPTIONS":
            response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours

    async def dispatch(self, request: Request, call_next):
        # Handle preflight OPTIONS requests - they need to return 200 with CORS headers
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            self._add_cors_headers(response, request)
            return response

        # Skip client header validation for certain paths
        request_path = request.url.path
        if any(request_path.startswith(skip_path) for skip_path in self.SKIP_PATHS):
            return await call_next(request)

        client = request.headers.get("client")
        token = request.headers.get("token")
        if not token:
            error_response = ErrorResponse(
                status="400",
                message="Missing required header: token",
                data={}
            )
            response = JSONResponse(error_response.model_dump(), status_code=400)
            # Add CORS headers to error responses
            self._add_cors_headers(response, request)
            return response
        
        if not client:
            error_response = ErrorResponse(
                status="400",
                message="Missing required header: client",
                data={}
            )
            response = JSONResponse(error_response.model_dump(), status_code=400)
            # Add CORS headers to error responses
            self._add_cors_headers(response, request)
            return response

        client_map = settings.DB_KEYS

        if client not in [*client_map, "admin"]:
            error_response = ErrorResponse(
                status="400",
                message="Invalid client header",
                data={}
            )
            response = JSONResponse(error_response.model_dump(), status_code=400)
            # Add CORS headers to error responses
            self._add_cors_headers(response, request)
            return response
        
        

        # Require a full URL entry in settings.DB_URLS for the client.
        db_urls = getattr(settings, "DB_URLS", None)
        if not db_urls or client not in db_urls:
            error_response = ErrorResponse(
                status="500",
                message="No full DB URL configured for client",
                data={}
            )
            response = JSONResponse(error_response.model_dump(), status_code=500)
            self._add_cors_headers(response, request)
            return response

        # prefer the explicit DB URL for this client
        client_db_url = db_urls[client]

        # try to reuse an engine from app.state cache (keyed by client)
        app = request.scope.get("app")
        if not hasattr(app.state, "engine_cache"):
            app.state.engine_cache = {}

        db_name = str(client_db_url).split("/")[-1]
        cache_key = client
        async_engine = None

        if cache_key in app.state.engine_cache:
            # check cached engine URL matches desired full URL (including password)
            cached_engine = app.state.engine_cache[cache_key]
            try:
                desired_url = make_url(str(client_db_url))
                cached_url = cached_engine.url
                if desired_url.render_as_string(hide_password=False) != cached_url.render_as_string(hide_password=False):
                    # dispose of the old engine and recreate below
                    try:
                        await cached_engine.dispose()
                    except Exception:
                        pass
                    async_engine = None
                else:
                    async_engine = cached_engine
            except Exception:
                # if anything goes wrong comparing, fall back to cached engine
                async_engine = cached_engine
        else:
            try:
                base_url = make_url(str(client_db_url))
            except Exception:
                error_response = ErrorResponse(
                    status="500",
                    message="Server DB configuration invalid",
                    data={}
                )
                response = JSONResponse(error_response.model_dump(), status_code=500)
                # Add CORS headers to error responses
                self._add_cors_headers(response, request)
                return response

            logger.info("Creating engine for %s (db=%s, using full DB_URLS entry)", client, db_name)
            async_engine = create_async_engine(
                base_url.render_as_string(hide_password=False), 
                echo=False, 
                future=True,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True
            )
            # verify connection immediately to fail fast on bad creds
            try:
                async with async_engine.connect() as conn:
                    await conn.execute(text("select 1"))
            except Exception as e:
                logger.error("DB connection test failed for client %s db %s: %s", client, db_name, e)
                try:
                    await async_engine.dispose()
                except Exception:
                    pass
                error_response = ErrorResponse(
                    status="500",
                    message="Cannot connect to database for client",
                    data={}
                )
                response = JSONResponse(error_response.model_dump(), status_code=500)
                # Add CORS headers to error responses
                self._add_cors_headers(response, request)
                return response

            app.state.engine_cache[cache_key] = async_engine

        # If cached engine was disposed due to mismatch, recreate it here (cache_key-aware)
        if cache_key in app.state.engine_cache and (async_engine is None):
            try:
                base_url = make_url(str(client_db_url))
            except Exception:
                error_response = ErrorResponse(
                    status="500",
                    message="Server DB configuration invalid",
                    data={}
                )
                response = JSONResponse(error_response.model_dump(), status_code=500)
                # Add CORS headers to error responses
                self._add_cors_headers(response, request)
                return response
            async_engine = create_async_engine(
                base_url.render_as_string(hide_password=False), 
                echo=False, 
                future=True,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True
            )
            try:
                async with async_engine.connect() as conn:
                    await conn.execute(text("select 1"))
            except Exception as e:
                logger.error("DB connection test failed when recreating engine for client %s db %s: %s", client, db_name, e)
                try:
                    await async_engine.dispose()
                except Exception:
                    pass
                error_response = ErrorResponse(
                    status="500",
                    message="Cannot connect to database for client",
                    data={}
                )
                response = JSONResponse(error_response.model_dump(), status_code=500)
                # Add CORS headers to error responses
                self._add_cors_headers(response, request)
                return response
            app.state.engine_cache[cache_key] = async_engine

        async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

        # attach to request.state for downstream dependencies (get_db will use it)
        request.state.async_engine = async_engine
        request.state.async_session = async_session
        request.state.client = client

        # Set client in contextvars for use in async functions
        client_context.set(client)
        
        # Call the next middleware/route handler
        response = await call_next(request)
        self._add_cors_headers(response, request)
        return response


# Authentication verification and session
security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        request: FastAPI request object
        credentials: HTTP Authorization credentials (Bearer token)
        db: Database session
        
    Returns:
        User object if authentication is successful
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Verify and decode token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user_id from payload
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user exists and is active
    from app.services.auth_service import verify_user_token
    user = await verify_user_token(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user is active.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if active
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.active:
        raise HTTPException(
            status_code=403,
            detail="Inactive user"
        )
    return current_user


def get_optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Optional authentication dependency.
    
    Args:
        request: FastAPI request object
        credentials: Optional HTTP Authorization credentials
        
    Returns:
        User ID string if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload:
        return payload.get("user_id")
    
    return None
