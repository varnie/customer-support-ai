import pytest
from app.models import Ticket, TicketStatus, TicketPriority


@pytest.mark.asyncio
async def test_ticket_model():
    # Example test for a Ticket model
    ticket = Ticket(subject="Test", body="This is a test ticket", customer_email="test@example.com")
    assert ticket.subject == "Test"
    assert ticket.body == "This is a test ticket"
    assert ticket.customer_email == "test@example.com"


@pytest.mark.asyncio
async def test_ticket_status_update():
    ticket = Ticket(subject="Update Status", body="Update status test", customer_email="update@example.com")
    ticket.status = TicketStatus.processed
    assert ticket.status == TicketStatus.processed


@pytest.mark.asyncio
async def test_ticket_priority_assignment():
    ticket = Ticket(subject="Priority Test", body="Testing priority assignment", customer_email="priority@example.com", priority=TicketPriority.high)
    assert ticket.priority == TicketPriority.high
