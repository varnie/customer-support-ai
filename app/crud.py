from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Ticket, TicketStatus
from app.schemas import TicketCreateRequest, TicketUpdateRequest


async def create_ticket(db: AsyncSession, ticket_data: TicketCreateRequest) -> Ticket:
    """
    Create a new ticket with the provided data.
    """
    new_ticket = Ticket(**ticket_data.model_dump())
    db.add(new_ticket)
    try:
        await db.commit()
        return new_ticket
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def get_ticket_by_id(db: AsyncSession, ticket_id: str) -> Ticket:
    """
    Retrieve a ticket by its ID.
    """
    query = select(Ticket).filter(Ticket.id == ticket_id)
    result = await db.execute(query)
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


async def get_all_tickets(db: AsyncSession, category: str = None, priority: str = None, status: str = None) -> list:
    """
    Retrieve all tickets with optional filters.
    """
    query = select(Ticket)
    if category:
        query = query.filter(Ticket.category == category)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if status:
        query = query.filter(Ticket.status == status)
    result = await db.execute(query)
    tickets = result.scalars().all()
    return tickets


async def update_ticket(db: AsyncSession, ticket_id: str, updates: TicketUpdateRequest) -> Ticket:
    """
    Update a ticket with the given updates.
    """
    query = select(Ticket).filter(Ticket.id == ticket_id)
    result = await db.execute(query)
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for var, value in updates.model_dump(exclude_unset=True).items():
        setattr(ticket, var, value)
    try:
        await db.commit()
        return ticket
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def delete_ticket(db: AsyncSession, ticket_id: str) -> None:
    """
    Delete a ticket by its ID.
    """
    query = select(Ticket).filter(Ticket.id == ticket_id)
    result = await db.execute(query)
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await db.delete(ticket)
    try:
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def get_all_unprocessed_tickets(db: AsyncSession) -> List[Ticket]:
    """
    Retrieve all tickets that have not been processed yet.
    This function assumes that there is a 'status' field in the 'Ticket' model
    that indicates whether a ticket has been processed or not.
    """
    query = select(Ticket).filter(Ticket.status == 'submitted')  # Adjust the filter as per your model's definition
    result = await db.execute(query)
    return result.scalars().all()


async def update_ticket_status(db: AsyncSession, ticket_id: int, status: TicketStatus):
    # Fetch the ticket by ID and update its status
    ticket = await db.get(Ticket, ticket_id)
    if ticket:
        ticket.status = status
        db.add(ticket)
        await db.commit()
