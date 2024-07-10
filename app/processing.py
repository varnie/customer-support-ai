import logging
from datetime import datetime

import redis
from rq import Queue
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import categorize_ticket, prioritize_ticket, generate_response, openai_model, anthropic_model
from app.config import Config
from app.crud import get_all_unprocessed_tickets, update_ticket, get_ticket_by_id
from app.database import AsyncSessionLocal
from app.models import TicketStatus
from app.schemas import TicketUpdateRequest

# Connect to Redis
redis_conn = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
queue = Queue(connection=redis_conn)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def enqueue_all_unprocessed_tickets(db: AsyncSession):
    """
    Fetch all unprocessed tickets, update their status to 'processing', and enqueue them for further processing.
    """
    tickets = await get_all_unprocessed_tickets(db)
    if not tickets:
        return None, 0  # No tickets to process

    job_ids = []
    for ticket in tickets:
        # Update the ticket status directly assuming db session handles transactions
        ticket.status = TicketStatus.processing
        db.add(ticket)
        await db.commit()  # Ensure the status update is committed before enqueueing

        job = queue.enqueue('app.processing.process_ticket', ticket.id)
        job_ids.append(job.id)

    return job_ids[0] if job_ids else None, len(tickets)


def enqueue_single_ticket(ticket_id: str):
    """
    Enqueue a single ticket for processing based on its ID.
    This function allows immediate processing of a newly created ticket.
    """
    logger.info(f"Enqueuing ticket with ID: {ticket_id} for processing")
    queue.enqueue('app.processing.process_ticket', ticket_id)
    return f"Ticket {ticket_id} enqueued for processing"


async def process_ticket(ticket_id: str):
    """
    Process a single ticket using AI services to categorize, prioritize,
    and generate an initial response.
    """
    async with AsyncSessionLocal() as db:
        ticket = await get_ticket_by_id(db, ticket_id)
        if not ticket:
            print(f"No ticket found with ID: {ticket_id}")
            return

        logger.info(f"Processing ticket: {ticket_id}")

        # AI Integration: Categorize, prioritize, and generate response
        category, category_confidence = await categorize_ticket(openai_model, ticket.subject, ticket.body)
        priority, priority_confidence = await prioritize_ticket(openai_model, ticket.subject, ticket.body)
        initial_response = await generate_response(anthropic_model, ticket.subject, ticket.body)

        # Prepare the ticket update payload
        ticket_update_data = TicketUpdateRequest(
            status=TicketStatus.processed,
            category=category,
            category_confidence=category_confidence,
            priority=priority,
            priority_confidence=priority_confidence,
            initial_response=initial_response,
            processed_at=datetime.utcnow()
        )

        # Update the ticket with new data
        await update_ticket(db, ticket.id, ticket_update_data)
        logger.info(f"Ticket processed: {ticket_id}")
