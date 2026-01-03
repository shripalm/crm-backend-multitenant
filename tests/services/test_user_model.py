import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from sqlalchemy import text
from app.main import app, defaultToken
from uuid import UUID


TEST_HEADERS = {
    "client": "test_db",
    "token": defaultToken
}

# -------------------------------
# Test user creation & listing
# -------------------------------
@pytest.mark.asyncio
async def test_create_users(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "email": "user123456789@example.com",
        "full_name": "Test User",
        "password": "strongpassword123",
        "team_name": "Team Alpha",
        "contact": "9999999999",
        "gender": "Male",
        "address": "123 Test Street"
    }

    
    create_response = await client.post(
            "/api/v1/users/",
            json=payload,
            headers=TEST_HEADERS
        )
    print("CREATE RESPONSE:", create_response.json())
    assert create_response.status_code == 200
    body = create_response.json().get("data", {})
    assert body.get("email") == payload["email"]

    # List users
@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, db_session: AsyncSession):
    list_response = await client.get(
            "/api/v1/users/",
            headers=TEST_HEADERS
        )
    print("LIST RESPONSE:", list_response.json())

    body = list_response.json()
    users = body.get("data", [])

    
    # Print for debugging
    print("LIST USERS RESPONSE:", body)
    for user in users:
        print(f"- {user['email']} | {user['full_name']}")
        # --- Assertions ---
    assert list_response.status_code == 200
    assert isinstance(users, list)
    assert len(users) >= 1
        



# 🔹 Existing records in DB
USER_ID = UUID("f2d35905-6f68-4cec-b94f-6e576104bdba")
ROLE_ID = UUID("0ba4e8fb-eb95-4c4c-a4bc-369e932d5019")  # replace


@pytest.mark.asyncio
async def test_add_role_to_user(
    client: AsyncClient,
    db_session: AsyncSession,
):
    
    response = await client.post(
        f"/api/v1/users/{USER_ID}/roles/{ROLE_ID}",
        headers=TEST_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "200"
    assert body["message"] == "Role assigned to user"
    assert "data" in body

    user = body["data"]

    # ---- User payload checks ----
    assert user["id"] == str(USER_ID)
    assert user["email"] is not None


    # -----------------------------
    # Verify role assigned
    # -----------------------------
    list_response = await client.get(
        "/api/v1/users/",
        headers=TEST_HEADERS,
    )

    assert list_response.status_code == 200

    users = list_response.json()["data"]
    user = next(u for u in users if u["id"] == str(USER_ID))

    role_ids = [r["id"] for r in user["roles"]]

    assert str(ROLE_ID) in role_ids

@pytest.mark.asyncio
async def test_create_user_invalid_email_format(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "email": "invalid-email",
        "full_name": "Test User",
        "password": "strongpassword123",
        "team_name": "Team Alpha",
        "contact": "9999999999",
        "gender": "Male",
        "address": "123 Test Street"
    }

    response = await client.post(
        "/api/v1/users/",
        json=payload,
        headers=TEST_HEADERS
    )

    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.asyncio
async def test_create_user_missing_email(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "full_name": "Test User",
        "password": "strongpassword123",
        "team_name": "Team Alpha",
        "contact": "9999999999",
        "gender": "Male",
        "address": "123 Test Street"
    }

    response = await client.post(
        "/api/v1/users/",
        json=payload,
        headers=TEST_HEADERS
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "email": "duplicate@example.com",
        "full_name": "Test User",
        "password": "strongpassword123",
        "team_name": "Team Alpha",
        "contact": "9999999999",
        "gender": "Male",
        "address": "123 Test Street"
    }

    # First creation
    await client.post(
        "/api/v1/users/",
        json=payload,
        headers=TEST_HEADERS
    )

    # Second creation with same email
    response = await client.post(
        "/api/v1/users/",
        json=payload,
        headers=TEST_HEADERS
    )

    assert response.status_code in (400, 409)

@pytest.mark.asyncio
async def test_create_user_contact_with_characters(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "email": "contactchars@example.com",
        "full_name": "Test User",
        "password": "strongpassword123",
        "team_name": "Team Alpha",
        "contact": "99999abcde",
        "gender": "Male",
        "address": "123 Test Street"
    }

    response = await client.post(
        "/api/v1/users/",
        json=payload,
        headers=TEST_HEADERS
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_user_missing_contact(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "email": "nocontact@example.com",
        "full_name": "Test User",
        "password": "strongpassword123",
        "team_name": "Team Alpha",
        "gender": "Male",
        "address": "123 Test Street"
    }

    response = await client.post(
        "/api/v1/users/",
        json=payload,
        headers=TEST_HEADERS
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_user_duplicate_contact(client: AsyncClient, db_session: AsyncSession):
    payload1 = {
        "email": "user1@example.com",
        "full_name": "User One",
        "password": "strongpassword123",
        "team_name": "Team Alpha",
        "contact": "8888888888",
        "gender": "Male",
        "address": "123 Test Street"
    }

    payload2 = {
        "email": "user2@example.com",
        "full_name": "User Two", 
        "password": "strongpassword123",
        "team_name": "Team Alpha",
        "contact": "8888888888",  # same contact
        "gender": "Male",
        "address": "123 Test Street"
    }

    await client.post(
        "/api/v1/users/",
        json=payload1,
        headers=TEST_HEADERS
    )

    response = await client.post(
        "/api/v1/users/",
        json=payload2,
        headers=TEST_HEADERS
    )

    assert response.status_code in (400, 409)
