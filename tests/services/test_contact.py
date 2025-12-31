import pytest
from httpx import AsyncClient
from app.main import app, defaultToken
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

TEST_HEADERS = {
    "client": "test_db",
    "token": defaultToken
}

@pytest.mark.asyncio
async def test_add_contact(client: AsyncClient, db_session: AsyncSession):
    """Test creating a new contact"""
    payload = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "contact_no": "1234567890",
        "city": "Mumbai",
        "state": "Maharashtra",
        "source": "Website",
        "project_name": "Project A",
        "property_type": "Apartment",
        "budget_range": "50L-1Cr"
    }

    response = await client.post("/api/v1/contacts/", 
            json=payload, headers=TEST_HEADERS
            )
    print("ADD CONTACT RESPONSE:", response.json())
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "200"
    assert "data" in body

    contact = body["data"]
    assert contact["name"] == payload["name"]
    assert contact["email"] == payload["email"]

    return contact["id"]  # return ID for other tests

@pytest.mark.asyncio
async def test_list_contacts(client: AsyncClient, db_session: AsyncSession ):
    """Test listing contacts"""
    response = await client.get("/api/v1/contacts/?page=1&size=10", headers=TEST_HEADERS)
    assert response.status_code == 200
    
    body = response.json()
    assert body["status"] == "200"
    assert "data" in body

    paginated_data = body["data"]
    assert "data" in paginated_data  # actual list of contacts
    assert "meta" in paginated_data  # pagination info

    contacts = paginated_data["data"]
    assert isinstance(contacts, list)

    # Optional: check at least one contact exists
    if contacts:
        contact = contacts[0]
        assert "id" in contact
        assert "name" in contact
        assert "email" in contact


@pytest.mark.asyncio
async def test_get_contact_by_id(client: AsyncClient, db_session: AsyncSession):
    """Test retrieving a single contact"""
    # Create a contact first
    payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "contact_no": "9876543210"
    }
    create_resp = await client.post("/api/v1/contacts/", json=payload, headers=TEST_HEADERS)
    contact_id = create_resp.json()["data"]["id"]

    response = await client.get(f"/api/v1/contacts/{contact_id}", headers=TEST_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == contact_id
    assert body["data"]["name"] == payload["name"]

