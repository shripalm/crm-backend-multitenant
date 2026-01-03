import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import defaultToken
from uuid import UUID

# Headers for testing
TEST_HEADERS = {
    "client": "test_db",      # matches middleware expectation
    "token": defaultToken
}

# -------------------------
# Test: Create & List Roles
# -------------------------
@pytest.mark.asyncio
async def test_create_and_list_role(client: AsyncClient, db_session: AsyncSession):
    """
    Test creating a role via POST and fetching via GET
    """

    payload = {
        "name": "presales_test33",
        "description": "Created via API test 1"
    }

    # --- Create Role ---
    create_response = await client.post(
        "/api/v1/roles/",
        json=payload,
        headers=TEST_HEADERS
    )

    print("CREATE RESPONSE:", create_response.json())
    assert create_response.status_code == 200
    created_role = create_response.json().get("data", {})
    assert created_role.get("name") == payload["name"]

    # --- List Roles ---
    list_response = await client.get(
        "/api/v1/roles/",
        headers=TEST_HEADERS
    )

    print("LIST RESPONSE:", list_response.json())
    body = list_response.json()
    roles = body.get("data", [])

    print("Roles in DB:")
    for role in roles:
        print(f"- {role['name']} | {role['description']}")

    # --- Assertions ---
    assert list_response.status_code == 200
    assert isinstance(roles, list)
    assert len(roles) >= 1
    assert any(role["name"] == payload["name"] for role in roles)


ROLE_ID = UUID("0ba4e8fb-eb95-4c4c-a4bc-369e932d5019")
PERMISSION_ID = UUID("8b62fc9c-1f7b-40e2-b21e-446501a6cd5b")

TEST_HEADERS = {
    "client": "test_db",
    "token": defaultToken
}

@pytest.mark.asyncio
async def test_assign_permission_to_role(client: AsyncClient, db_session: AsyncSession):
    """Test assigning a permission to a role"""

    response = await client.post(
        f"/api/v1/roles/{ROLE_ID}/permissions/{PERMISSION_ID}",
        headers=TEST_HEADERS
    )

    # ---- Basic response checks ----
    assert response.status_code == 200
    body = response.json()
    
    # Your StandardResponse typically contains 'status', 'message', 'data'
    assert body["status"] == "200"
    assert body["message"] == "Permission assigned successfully"  # adjust if different
    assert "data" in body
'''
    # ---- Verify that the role now has the permission ----
    role_data = body["data"]
    assigned_permission_ids = [p["id"] for p in role_data.get("permissions", [])]
    assert str(PERMISSION_ID) in assigned_permission_ids
'''

@pytest.mark.asyncio
async def test_list_permissions(client: AsyncClient, db_session: AsyncSession):
    """Test retrieving all permissions"""
    
    response = await client.get(
        "/api/v1/permissions/",
        headers=TEST_HEADERS
    )

    assert response.status_code == 200

    body = response.json()
    # StandardResponse typically has: status, message, data
    assert body["status"] == "200"
    assert body["message"] == "Permissions retrieved"
    assert "data" in body

    permissions = body["data"]
    assert isinstance(permissions, list)
    print("\nPermissions retrieved:")
    for perm in permissions:
        print(f"ID: {perm['id']}, Name: {perm['name']}, Label: {perm['label']}, Description: {perm.get('description')}, Created At: {perm.get('created_at')}")

    # Optional: check at least one permission exists
    if permissions:
        perm = permissions[0]
        assert "id" in perm
        assert "name" in perm
        assert "label" in perm
