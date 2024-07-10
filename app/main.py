import logging
from typing import List, Optional

from fastapi import FastAPI, Depends, status
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.crud import create_ticket, get_ticket_by_id, get_all_tickets
from app.database import AsyncSessionLocal
from app.processing import enqueue_all_unprocessed_tickets, enqueue_single_ticket
from app.schemas import TicketCreateRequest, TicketResponse, TicketCreationResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse({"detail": exc.errors()}, status_code=400)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse({"detail": "An unexpected error occurred."}, status_code=500)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status code: {response.status_code}")
    return response


# Dependency to get database session
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/ticket", response_model=TicketCreationResponse, status_code=status.HTTP_201_CREATED)
async def post_ticket(ticket: TicketCreateRequest, db: AsyncSession = Depends(get_db_session)):
    db_ticket = await create_ticket(db, ticket)
    enqueue_single_ticket(db_ticket.id)

    # Construct the response model to return
    return TicketCreationResponse(
        ticket_id=db_ticket.id,
        status='submitted',  # Assuming 'submitted' is an appropriate status after creation
        message='Ticket submitted successfully and queued for processing'
    )


@app.get("/ticket/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, db: AsyncSession = Depends(get_db_session)):
    db_ticket = await get_ticket_by_id(db, ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket


@app.get("/tickets", response_model=List[TicketResponse])
async def get_tickets(category: Optional[str] = None, priority: Optional[str] = None, status: Optional[str] = None,
                      db: AsyncSession = Depends(get_db_session)):
    tickets = await get_all_tickets(db, category, priority, status)
    return tickets


@app.post("/process")
async def post_process(db: AsyncSession = Depends(get_db_session)):
    """
    Manually trigger processing of all unprocessed tickets.
    """
    job_id, ticket_count = await enqueue_all_unprocessed_tickets(db)
    if not job_id:
        return {"message": "No unprocessed tickets to process", "job_id": None}
    return {"message": f"Processing started for {ticket_count} tickets", "job_id": job_id}
