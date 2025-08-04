import pytest
from datetime import date, datetime
from app.database import reset_db
from app.investment_service import InvestmentService
from app.models import InvestmentIdeaCreate, InvestmentIdeaUpdate, InvestmentStatus


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


class TestInvestmentService:
    """Test suite for InvestmentService class."""

    def test_create_investment_idea_minimal(self, new_db):
        """Test creating an investment idea with minimal required fields."""
        idea_data = InvestmentIdeaCreate(title="Tesla Stock Analysis")

        result = InvestmentService.create_investment_idea(idea_data)

        assert result.id is not None
        assert result.title == "Tesla Stock Analysis"
        assert result.description == ""
        assert result.idea_date == date.today()
        assert result.status == InvestmentStatus.RESEARCHING
        assert result.notes == ""
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)

    def test_create_investment_idea_full(self, new_db):
        """Test creating an investment idea with all fields provided."""
        specific_date = date(2024, 1, 15)
        idea_data = InvestmentIdeaCreate(
            title="Apple AAPL Analysis",
            description="Looking into Apple's growth potential in AI",
            idea_date=specific_date,
            status=InvestmentStatus.WATCHLIST,
            notes="P/E ratio looks attractive at current levels",
        )

        result = InvestmentService.create_investment_idea(idea_data)

        assert result.title == "Apple AAPL Analysis"
        assert result.description == "Looking into Apple's growth potential in AI"
        assert result.idea_date == specific_date
        assert result.status == InvestmentStatus.WATCHLIST
        assert result.notes == "P/E ratio looks attractive at current levels"

    def test_get_all_investment_ideas_empty(self, new_db):
        """Test getting all investment ideas when database is empty."""
        result = InvestmentService.get_all_investment_ideas()
        assert result == []

    def test_get_all_investment_ideas_ordered(self, new_db):
        """Test that investment ideas are returned in descending creation order."""
        # Create multiple ideas
        InvestmentService.create_investment_idea(InvestmentIdeaCreate(title="First Idea"))
        InvestmentService.create_investment_idea(InvestmentIdeaCreate(title="Second Idea"))
        InvestmentService.create_investment_idea(InvestmentIdeaCreate(title="Third Idea"))

        result = InvestmentService.get_all_investment_ideas()

        assert len(result) == 3
        # Should be ordered by creation time descending (newest first)
        assert result[0].title == "Third Idea"
        assert result[1].title == "Second Idea"
        assert result[2].title == "First Idea"

    def test_get_investment_idea_by_id_existing(self, new_db):
        """Test getting an investment idea by valid ID."""
        created_idea = InvestmentService.create_investment_idea(InvestmentIdeaCreate(title="Bitcoin Analysis"))

        result = InvestmentService.get_investment_idea_by_id(created_idea.id)

        assert result is not None
        assert result.id == created_idea.id
        assert result.title == "Bitcoin Analysis"

    def test_get_investment_idea_by_id_nonexistent(self, new_db):
        """Test getting an investment idea by non-existent ID."""
        result = InvestmentService.get_investment_idea_by_id(999)
        assert result is None

    def test_update_investment_idea_partial(self, new_db):
        """Test updating some fields of an investment idea."""
        created_idea = InvestmentService.create_investment_idea(
            InvestmentIdeaCreate(title="Original Title", status=InvestmentStatus.RESEARCHING)
        )

        update_data = InvestmentIdeaUpdate(title="Updated Title", status=InvestmentStatus.INVESTED)

        result = InvestmentService.update_investment_idea(created_idea.id, update_data)

        assert result is not None
        assert result.title == "Updated Title"
        assert result.status == InvestmentStatus.INVESTED
        assert result.description == ""  # Should remain unchanged
        assert result.updated_at > result.created_at

    def test_update_investment_idea_all_fields(self, new_db):
        """Test updating all fields of an investment idea."""
        created_idea = InvestmentService.create_investment_idea(InvestmentIdeaCreate(title="Original"))

        new_date = date(2024, 6, 15)
        update_data = InvestmentIdeaUpdate(
            title="Completely Updated",
            description="New description",
            idea_date=new_date,
            status=InvestmentStatus.REJECTED,
            notes="Updated notes",
        )

        result = InvestmentService.update_investment_idea(created_idea.id, update_data)

        assert result is not None
        assert result.title == "Completely Updated"
        assert result.description == "New description"
        assert result.idea_date == new_date
        assert result.status == InvestmentStatus.REJECTED
        assert result.notes == "Updated notes"

    def test_update_investment_idea_nonexistent(self, new_db):
        """Test updating a non-existent investment idea."""
        update_data = InvestmentIdeaUpdate(title="Won't work")

        result = InvestmentService.update_investment_idea(999, update_data)
        assert result is None

    def test_delete_investment_idea_existing(self, new_db):
        """Test deleting an existing investment idea."""
        created_idea = InvestmentService.create_investment_idea(InvestmentIdeaCreate(title="To be deleted"))

        result = InvestmentService.delete_investment_idea(created_idea.id)
        assert result is True

        # Verify it's actually deleted
        deleted_idea = InvestmentService.get_investment_idea_by_id(created_idea.id)
        assert deleted_idea is None

    def test_delete_investment_idea_nonexistent(self, new_db):
        """Test deleting a non-existent investment idea."""
        result = InvestmentService.delete_investment_idea(999)
        assert result is False

    def test_get_ideas_by_status_empty(self, new_db):
        """Test filtering by status when no ideas exist."""
        result = InvestmentService.get_ideas_by_status(InvestmentStatus.INVESTED)
        assert result == []

    def test_get_ideas_by_status_filtered(self, new_db):
        """Test filtering investment ideas by status."""
        # Create ideas with different statuses
        InvestmentService.create_investment_idea(
            InvestmentIdeaCreate(title="Research Idea", status=InvestmentStatus.RESEARCHING)
        )
        InvestmentService.create_investment_idea(
            InvestmentIdeaCreate(title="Watchlist Idea", status=InvestmentStatus.WATCHLIST)
        )
        InvestmentService.create_investment_idea(
            InvestmentIdeaCreate(title="Another Watchlist", status=InvestmentStatus.WATCHLIST)
        )
        InvestmentService.create_investment_idea(
            InvestmentIdeaCreate(title="Invested Idea", status=InvestmentStatus.INVESTED)
        )

        # Test filtering by WATCHLIST
        watchlist_ideas = InvestmentService.get_ideas_by_status(InvestmentStatus.WATCHLIST)
        assert len(watchlist_ideas) == 2
        assert all(idea.status == InvestmentStatus.WATCHLIST for idea in watchlist_ideas)

        # Test filtering by INVESTED
        invested_ideas = InvestmentService.get_ideas_by_status(InvestmentStatus.INVESTED)
        assert len(invested_ideas) == 1
        assert invested_ideas[0].title == "Invested Idea"

        # Test filtering by REJECTED (should be empty)
        rejected_ideas = InvestmentService.get_ideas_by_status(InvestmentStatus.REJECTED)
        assert len(rejected_ideas) == 0

    def test_create_with_long_strings(self, new_db):
        """Test creating investment idea with maximum length strings."""
        long_title = "A" * 200
        long_description = "B" * 2000
        long_notes = "C" * 5000

        idea_data = InvestmentIdeaCreate(title=long_title, description=long_description, notes=long_notes)

        result = InvestmentService.create_investment_idea(idea_data)

        assert result.title == long_title
        assert result.description == long_description
        assert result.notes == long_notes

    def test_update_with_none_values(self, new_db):
        """Test updating with None values doesn't change existing data."""
        created_idea = InvestmentService.create_investment_idea(
            InvestmentIdeaCreate(title="Original Title", description="Original Description", notes="Original Notes")
        )

        # Update with only status, other fields should remain unchanged
        update_data = InvestmentIdeaUpdate(status=InvestmentStatus.INVESTED)

        result = InvestmentService.update_investment_idea(created_idea.id, update_data)

        assert result is not None
        assert result.title == "Original Title"  # Should remain unchanged
        assert result.description == "Original Description"  # Should remain unchanged
        assert result.notes == "Original Notes"  # Should remain unchanged
        assert result.status == InvestmentStatus.INVESTED  # Should be updated
