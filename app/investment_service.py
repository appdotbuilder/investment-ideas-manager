from datetime import date, datetime
from typing import Optional
from sqlmodel import select, desc
from app.database import get_session
from app.models import InvestmentIdea, InvestmentIdeaCreate, InvestmentIdeaUpdate, InvestmentIdeaRead, InvestmentStatus


class InvestmentService:
    """Service class for managing investment ideas."""

    @staticmethod
    def create_investment_idea(idea_data: InvestmentIdeaCreate) -> InvestmentIdeaRead:
        """Create a new investment idea."""
        with get_session() as session:
            # Set default date if not provided
            if idea_data.idea_date is None:
                idea_data.idea_date = date.today()

            investment_idea = InvestmentIdea(
                title=idea_data.title,
                description=idea_data.description,
                idea_date=idea_data.idea_date,
                status=idea_data.status,
                notes=idea_data.notes,
            )

            session.add(investment_idea)
            session.commit()
            session.refresh(investment_idea)

            return InvestmentIdeaRead.model_validate(investment_idea)

    @staticmethod
    def get_all_investment_ideas() -> list[InvestmentIdeaRead]:
        """Get all investment ideas ordered by creation date descending."""
        with get_session() as session:
            statement = select(InvestmentIdea).order_by(desc(InvestmentIdea.created_at))
            ideas = session.exec(statement).all()
            return [InvestmentIdeaRead.model_validate(idea) for idea in ideas]

    @staticmethod
    def get_investment_idea_by_id(idea_id: int) -> Optional[InvestmentIdeaRead]:
        """Get a specific investment idea by ID."""
        with get_session() as session:
            idea = session.get(InvestmentIdea, idea_id)
            if idea is None:
                return None
            return InvestmentIdeaRead.model_validate(idea)

    @staticmethod
    def update_investment_idea(idea_id: int, update_data: InvestmentIdeaUpdate) -> Optional[InvestmentIdeaRead]:
        """Update an existing investment idea."""
        with get_session() as session:
            idea = session.get(InvestmentIdea, idea_id)
            if idea is None:
                return None

            # Update only fields that are provided
            for field, value in update_data.model_dump(exclude_unset=True).items():
                setattr(idea, field, value)

            idea.updated_at = datetime.utcnow()
            session.add(idea)
            session.commit()
            session.refresh(idea)

            return InvestmentIdeaRead.model_validate(idea)

    @staticmethod
    def delete_investment_idea(idea_id: int) -> bool:
        """Delete an investment idea by ID."""
        with get_session() as session:
            idea = session.get(InvestmentIdea, idea_id)
            if idea is None:
                return False

            session.delete(idea)
            session.commit()
            return True

    @staticmethod
    def get_ideas_by_status(status: InvestmentStatus) -> list[InvestmentIdeaRead]:
        """Get all investment ideas filtered by status."""
        with get_session() as session:
            statement = (
                select(InvestmentIdea).where(InvestmentIdea.status == status).order_by(desc(InvestmentIdea.created_at))
            )
            ideas = session.exec(statement).all()
            return [InvestmentIdeaRead.model_validate(idea) for idea in ideas]
