import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_ticket(client):
    response = await client.post("/ticket", json={
        "subject": "Test Ticket",
        "body": "This is a test ticket body.",
        "customer_email": "test@example.com"
    })
    assert response.status_code == 201
    assert response.json()["status"] == "submitted"


@pytest.mark.asyncio
async def test_get_ticket_by_id(client):
    # Create a ticket first to ensure there is a ticket to retrieve
    create_response = await client.post("/ticket", json={
        "subject": "Ticket for ID Test",
        "body": "This ticket is for testing get by ID.",
        "customer_email": "idtest@example.com"
    })
    ticket_id = create_response.json()["ticket_id"]

    # Now, retrieve the ticket by ID
    response = await client.get(f"/ticket/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


@pytest.mark.asyncio
async def test_list_tickets(client):
    response = await client.get("/tickets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_process_tickets(client):
    response = await client.post("/process")
    assert response.status_code == 200
    assert "message" in response.json()
