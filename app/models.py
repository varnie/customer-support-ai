import enum
import uuid

from sqlalchemy import Column, String, Text, Enum, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TicketStatus(enum.Enum):
    submitted = 'submitted'
    processing = 'processing'
    processed = 'processed'


class TicketPriority(enum.Enum):
    high = 'high'
    medium = 'medium'
    low = 'low'


class TicketCategory(enum.Enum):
    account_access = 'account_access'
    payment_issue = 'payment_issue'
    feature_request = 'feature_request'
    technical_problem = 'technical_problem'
    other = 'other'


class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    customer_email = Column(String(255), nullable=False)
    category = Column(Enum(TicketCategory), nullable=True)
    priority = Column(Enum(TicketPriority), nullable=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.submitted, nullable=False)
    initial_response = Column(Text, nullable=True)
    category_confidence = Column(Float, nullable=True)
    priority_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Ticket {self.id} - {self.subject}>"
