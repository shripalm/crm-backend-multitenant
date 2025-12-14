from fastapi import Depends, FastAPI, HTTPException, Header, Query
from fastapi.exceptions import RequestValidationError
 
from app.api.v1.routers import health
from app.api.v1.routers import dev_settings
from app.api.v1.routers import projects
from app.api.v1.routers import property
from app.api.v1.routers import upload

from app.middleware.password_middleware import verify_credentials

from app.core.config import settings
from app.utils.logging import logger

from app.middleware.client_middleware import ClientHeaderMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.api.v1.routers import user, role, permission, contact, callreport, task, auth, admin_auth, agent_auth, lead, visibility, sitevisit, booking



from app.utils.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

async def get_client_header(client: Optional[str] = Header(default="godrej", description="Client key, e.g. godrej")):
    return client

defaultToken = "eyJraWQiOiJyMGh3SC1GVTRZOFJWbVVGd19tbUNXQ0RJSWpVUW5neTRqSlZscmx3S2JVIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULm1JNVNzTThBMEhVcmZ3RF9DVlZKbG1vX3cwWGthc2Y2Z2VyUUxaNlhyREEiLCJpc3MiOiJodHRwczovL215YXBwcy10ZXN0LmRlbnRzdS5jb20vb2F1dGgyL2RlZmF1bHQiLCJhdWQiOiJhcGk6Ly9kZWZhdWx0IiwiaWF0IjoxNzU5ODIxMjUzLCJleHAiOjE3NTk4MjQ4NTMsImNpZCI6IjBvYWhra2ExcXYwaFNWajEyMGk3IiwidWlkIjoiMDB1aGtxYmR3aDE5THRtekgwaTciLCJzY3AiOlsicHJvZmlsZSIsImVtYWlsIiwib3BlbmlkIl0sImF1dGhfdGltZSI6MTc1OTgyMDg1NSwic3ViIjoiU2Fuaml2LlN1dGFyQG1lcmtsZS5jb20iLCJQcm9yb2tfRGV2IjoiU2Fuaml2IFN1dGFyIiwiZ3JvdXBzIjpbIk9rdGEtSW50ZXJuYWwtU0ctR3JvdXBNZW1iZXJBZG1pbi1NdWx0aXRlbmFudCBtZWRpYSBzcGFyayIsIkV2ZXJ5b25lIiwiT3JnMk9yZy1GZWRVc2Vycy1UZXN0IiwiT2t0YS1JbnRlcm5hbC1TRy1BcHAtTXVsdGl0ZW5hbnQgbWVkaWEgc3BhcmsiLCJPa3RhLUludGVybmFsLVNHLUFwcC1NdWx0aXRlbmFudCBtZWRpYSBzcGFyay1BZG1pbiIsImRlbnRzdSBTdGFmZiIsIk9rdGEtSW50ZXJuYWwtU0ctQXBwLU11bHRpdGVuYW50IG1lZGlhIHNwYXJrLUxlbm92byIsIk9rdGEgR3JvdXAgREFOIEFEIFVzZXJzIl0sImRlcGFydG1lbnQiOiJJTkQ6Q1hNOkVuZ2luZWVyaW5nKFJhaHVsIFlhZGF2ICg2MzE0OTA2MSkpIn0.K6U5eTxhzIDUVgNZ56mLRBLVItCyOC7DjlkuP2ggUuSgnhKIXkEBL7kt1DwF2w8IBpmoHDXNCB5cvyJW36cAQBpSFkTTqMH7--UCpxvFDBMFHTtN7Tum_ya4lq3DkqhW7h0dkOxeud2WdTyUXALOOdvwHcQi4R4yj-DZtIYJ0Z39nfoa8772Bwpz3y8DpcSkGcfEZpTLW8fb3paClifwlox7j9EiISTv0o5vYp7PONubvQpkc0OM0Y_uA9s2jxCFsPauuHOo8avajY8ncg7ty1dystQTX6nrgWSIQok72EYZn_9wzCvQE-P-k21Io6M7de25lyMGtpKt0Ja94Dzfeg"
async def get_token(token: Optional[str] = Header(default=defaultToken, description="Access Token")):
    return token

app = FastAPI(
    title=settings.PROJECT_NAME, 
    dependencies=[
        Depends(get_client_header),
        Depends(get_token),
    ],
    root_path=settings.STAGE_PATH
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("App running", stage=settings.STAGE_PATH)

# Add exception handlers for standardized error responses
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register middleware that validates the `client` header on all requests
app.add_middleware(LoggingMiddleware)
app.add_middleware(ClientHeaderMiddleware)

 
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(dev_settings.router, prefix="/api/settings", tags=["settings"], dependencies=[Depends(verify_credentials)])

# Authentication
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(admin_auth.router, prefix="/api/v1/admin/auth", tags=["Admin Authentication"])
app.include_router(agent_auth.router, prefix="/api/v1/agents/auth", tags=["Agent Authentication"])

app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects and Properties"]) 
app.include_router(property.router, prefix="/api/v1/property", tags=["Projects and Properties"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["File Upload"])

app.include_router(user.router, prefix="/api/v1/users", tags=["Users and RBAC"])
app.include_router(task.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(role.router, prefix="/api/v1/roles", tags=["Users and RBAC"])
app.include_router(permission.router, prefix="/api/v1/permissions", tags=["Users and RBAC"])
app.include_router(contact.router, prefix="/api/v1/contacts", tags=["Contacts"])
app.include_router(callreport.router, prefix="/api/v1/call-reports", tags=["Call Reports"])
app.include_router(sitevisit.router, prefix="/api/v1/site-visit", tags=['Site Visit'])
app.include_router(booking.router, prefix="/api/v1/bookings", tags=['Bookings'])
app.include_router(lead.router, prefix="/api/v1/leads", tags=["Leads"])
app.include_router(visibility.router, prefix="/api/v1/visibility", tags=["User Visibility"])

from app.db.listeners import before_cursor_execute, after_cursor_execute
from sqlalchemy import event
from app.db.session import default_engine as engine

@app.on_event("startup")
async def on_startup():
    # Register SQLAlchemy event listeners
    event.listen(engine.sync_engine, "before_cursor_execute", before_cursor_execute)
    event.listen(engine.sync_engine, "after_cursor_execute", after_cursor_execute)
    # can perform startup tasks here (e.g. connection warmup)
    pass


@app.on_event("shutdown")
async def on_shutdown():
    # clean up cached engines created per client
    state = getattr(app, "state", None)
    if state and hasattr(state, "engine_cache"):
        for engine in list(state.engine_cache.values()):
            try:
                await engine.dispose()
            except Exception:
                pass
