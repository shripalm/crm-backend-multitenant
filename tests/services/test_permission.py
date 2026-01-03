import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.main import app
from app.db.session import get_db
from app.schemas.permission_schema import PermissionCreate
from app.main import app, defaultToken
# Optional: mock DB session for testing if needed
# from tests.db.test_session import db_session

TEST_HEADERS = {
    "client": "test_db",
    "token": defaultToken
}


@pytest.mark.asyncio
async def test_create_permission(client: AsyncClient, db_session: AsyncSession):
    """Test creating a permission via API"""

    payload = {
        "name": "name 2",
        "label": "create name 2",
        "description": "Created for pytest"
    }

    response = await client.post("/api/v1/permissions/", json=payload, headers=TEST_HEADERS)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "200"
    assert body["message"] == "Permission created"
    assert "data" in body

    perm = body["data"]
    assert perm["name"] == payload["name"]
    assert perm["label"] == payload["label"]
    assert perm["description"] == payload["description"]
    assert UUID(perm["id"])  # ID is a valid UUID


@pytest.mark.asyncio
async def test_list_permissions(client: AsyncClient, db_session: AsyncSession):
    """Test listing permissions via API"""

    response = await client.get("/api/v1/permissions/", headers=TEST_HEADERS)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "200"
    assert body["message"] == "Permissions retrieved"
    assert "data" in body

    perms = body["data"]
    assert isinstance(perms, list)
    for perm in perms:
        assert "id" in perm
        assert "name" in perm
        assert "label" in perm
