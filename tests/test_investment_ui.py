import pytest
from app.database import reset_db
from app.investment_service import InvestmentService
from app.models import InvestmentIdeaCreate, InvestmentStatus


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


class TestInvestmentUIServiceIntegration:
    """Test integration between UI and service layer without complex UI interactions."""

    def test_service_integration_create_and_retrieve(self, new_db):
        """Test that the service layer properly handles investment idea creation and retrieval."""
        # Test creating an idea like the UI would
        idea_data = InvestmentIdeaCreate(
            title="Tesla Stock Analysis",
            description="Electric vehicle market analysis",
            status=InvestmentStatus.WATCHLIST,
            notes="Strong growth potential",
        )

        InvestmentService.create_investment_idea(idea_data)

        # Verify it can be retrieved (like the UI list would)
        all_ideas = InvestmentService.get_all_investment_ideas()
        assert len(all_ideas) == 1
        assert all_ideas[0].title == "Tesla Stock Analysis"
        assert all_ideas[0].status == InvestmentStatus.WATCHLIST

    def test_service_integration_filter_by_status(self, new_db):
        """Test status filtering functionality that the UI uses."""
        # Create ideas with different statuses
        InvestmentService.create_investment_idea(
            InvestmentIdeaCreate(title="Research Item", status=InvestmentStatus.RESEARCHING)
        )
        InvestmentService.create_investment_idea(
            InvestmentIdeaCreate(title="Watchlist Item", status=InvestmentStatus.WATCHLIST)
        )
        InvestmentService.create_investment_idea(
            InvestmentIdeaCreate(title="Invested Item", status=InvestmentStatus.INVESTED)
        )

        # Test filtering like the UI would
        watchlist_ideas = InvestmentService.get_ideas_by_status(InvestmentStatus.WATCHLIST)
        invested_ideas = InvestmentService.get_ideas_by_status(InvestmentStatus.INVESTED)

        assert len(watchlist_ideas) == 1
        assert watchlist_ideas[0].title == "Watchlist Item"
        assert len(invested_ideas) == 1
        assert invested_ideas[0].title == "Invested Item"

    def test_service_integration_edit_workflow(self, new_db):
        """Test the edit workflow that the UI dialogs would use."""
        # Create idea
        created_idea = InvestmentService.create_investment_idea(
            InvestmentIdeaCreate(title="Original Title", status=InvestmentStatus.RESEARCHING)
        )

        # Simulate edit dialog workflow
        idea_to_edit = InvestmentService.get_investment_idea_by_id(created_idea.id)
        assert idea_to_edit is not None

        # Update like the edit dialog would
        from app.models import InvestmentIdeaUpdate

        update_data = InvestmentIdeaUpdate(title="Updated Title", status=InvestmentStatus.INVESTED)

        updated_idea = InvestmentService.update_investment_idea(created_idea.id, update_data)
        assert updated_idea is not None
        assert updated_idea.title == "Updated Title"
        assert updated_idea.status == InvestmentStatus.INVESTED

    def test_service_integration_delete_workflow(self, new_db):
        """Test the delete workflow that the UI would use."""
        # Create idea
        created_idea = InvestmentService.create_investment_idea(InvestmentIdeaCreate(title="To Be Deleted"))

        # Verify it exists
        idea_exists = InvestmentService.get_investment_idea_by_id(created_idea.id)
        assert idea_exists is not None

        # Delete like the UI would
        delete_success = InvestmentService.delete_investment_idea(created_idea.id)
        assert delete_success is True

        # Verify it's gone
        deleted_idea = InvestmentService.get_investment_idea_by_id(created_idea.id)
        assert deleted_idea is None
