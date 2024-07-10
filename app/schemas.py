import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TicketStatus(str, enum.Enum):
    submitted = 'submitted'
    processing = 'processing'
    processed = 'processed'


class TicketPriority(str, enum.Enum):
    high = 'high'
    medium = 'medium'
    low = 'low'


class TicketCategory(str, enum.Enum):
    account_access = 'account_access'
    payment_issue = 'payment_issue'
    feature_request = 'feature_request'
    technical_problem = 'technical_problem'
    other = 'other'


# Schema for ticket submission
class TicketCreateRequest(BaseModel):
    subject: str = Field(..., example="Cannot access my account")
    body: str = Field(...,
                      example="I've been trying to log in for the past hour but keep getting an 'invalid credentials' error.")
    customer_email: EmailStr = Field(..., example="user@example.com")


# Schema for ticket output
class TicketResponse(BaseModel):
    id: UUID
    subject: str
    body: str
    customer_email: EmailStr
    status: TicketStatus
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    initial_response: Optional[str] = None
    category_confidence: Optional[float] = None
    priority_confidence: Optional[float] = None
    created_at: datetime
    processed_at: Optional[datetime] = None


class TicketCreationResponse(BaseModel):
    ticket_id: UUID
    status: TicketStatus
    message: str


# Schema for updating a ticket's status
class TicketUpdateRequest(BaseModel):
    status: TicketStatus
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    initial_response: Optional[str] = None
    category_confidence: Optional[float] = None
    priority_confidence: Optional[float] = None
    processed_at: Optional[datetime] = None
