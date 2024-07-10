import uuid
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import Ticket, TicketStatus
from app.processing import enqueue_all_unprocessed_tickets, enqueue_single_ticket, process_ticket


@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_enqueue_all_unprocessed_tickets_no_tickets(db_session: AsyncSession):
    with patch('app.processing.get_all_unprocessed_tickets', AsyncMock(return_value=[])):
        job_id, ticket_count = await enqueue_all_unprocessed_tickets(db_session)
        assert job_id is None
        assert ticket_count == 0


@pytest.mark.asyncio
async def test_enqueue_all_unprocessed_tickets_with_tickets(db_session: AsyncSession):
    mock_tickets = [
        Ticket(
            id=uuid.uuid4(),
            subject="Test Subject 1",
            body="Test Body 1",
            customer_email="test1@example.com",
            status=TicketStatus.submitted
        ),
        Ticket(
            id=uuid.uuid4(),
            subject="Test Subject 2",
            body="Test Body 2",
            customer_email="test2@example.com",
            status=TicketStatus.submitted
        )
    ]
    with patch('app.processing.get_all_unprocessed_tickets', AsyncMock(return_value=mock_tickets)), \
         patch('app.processing.queue', MagicMock()) as mock_queue:
        job_id, ticket_count = await enqueue_all_unprocessed_tickets(db_session)
        assert ticket_count == len(mock_tickets)
        assert mock_queue.enqueue.call_count == len(mock_tickets)


@pytest.mark.asyncio
async def test_enqueue_single_ticket():
    ticket_id = str(uuid.uuid4())
    with patch('app.processing.queue.enqueue', new_callable=MagicMock) as mock_enqueue:
        enqueue_single_ticket(ticket_id)
        mock_enqueue.assert_called_once_with('app.processing.process_ticket', ticket_id)


@pytest.mark.asyncio
async def test_process_ticket(db_session: AsyncSession):
    ticket_id = str(uuid.uuid4())
    mock_ticket = Ticket(id=ticket_id, subject="Test", body="Test body", status=TicketStatus.submitted)
    with patch('app.processing.get_ticket_by_id', AsyncMock(return_value=mock_ticket)), \
         patch('app.processing.categorize_ticket', AsyncMock(return_value=("technical_problem", 0.95))), \
         patch('app.processing.prioritize_ticket', AsyncMock(return_value=("high", 0.95))), \
         patch('app.processing.generate_response', AsyncMock(return_value="Test response")), \
         patch('app.processing.update_ticket', new_callable=AsyncMock) as mock_update_ticket:
        await process_ticket(ticket_id)
        mock_update_ticket.assert_called_once()
