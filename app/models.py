from sqlmodel import SQLModel, Field
from datetime import datetime, date
from typing import Optional
from enum import Enum


class InvestmentStatus(str, Enum):
    """Enum for investment idea status options."""

    RESEARCHING = "Researching"
    WATCHLIST = "Watchlist"
    INVESTED = "Invested"
    REJECTED = "Rejected"


class InvestmentIdea(SQLModel, table=True):
    """Investment idea model for storing investment opportunities and research."""

    __tablename__ = "investment_ideas"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, description="Title of the investment idea")
    description: str = Field(
        default="", max_length=2000, description="Detailed description of the investment opportunity"
    )
    idea_date: date = Field(default_factory=date.today, description="Date when the idea was recorded")
    status: InvestmentStatus = Field(
        default=InvestmentStatus.RESEARCHING, description="Current status of the investment idea"
    )
    notes: str = Field(default="", max_length=5000, description="Additional notes and research details")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas for validation and API operations
class InvestmentIdeaCreate(SQLModel, table=False):
    """Schema for creating new investment ideas."""

    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    idea_date: Optional[date] = Field(default=None)
    status: InvestmentStatus = Field(default=InvestmentStatus.RESEARCHING)
    notes: str = Field(default="", max_length=5000)


class InvestmentIdeaUpdate(SQLModel, table=False):
    """Schema for updating existing investment ideas."""

    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    idea_date: Optional[date] = Field(default=None)
    status: Optional[InvestmentStatus] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=5000)


class InvestmentIdeaRead(SQLModel, table=False):
    """Schema for reading investment ideas with all fields."""

    id: int
    title: str
    description: str
    idea_date: date
    status: InvestmentStatus
    notes: str
    created_at: datetime
    updated_at: datetime
