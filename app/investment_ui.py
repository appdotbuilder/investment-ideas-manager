from datetime import date
from nicegui import ui
from app.investment_service import InvestmentService
from app.models import InvestmentIdeaCreate, InvestmentIdeaUpdate, InvestmentStatus, InvestmentIdeaRead
import logging

logger = logging.getLogger(__name__)


def create():
    """Create the investment ideas management pages."""

    # Apply modern theme
    ui.colors(
        primary="#2563eb",
        secondary="#64748b",
        accent="#10b981",
        positive="#10b981",
        negative="#ef4444",
        warning="#f59e0b",
        info="#3b82f6",
    )

    @ui.page("/")
    def investment_ideas_page():
        # Header
        with ui.row().classes("w-full justify-between items-center mb-8"):
            ui.label("💡 Investment Ideas Tracker").classes("text-3xl font-bold text-gray-800")
            ui.label("Record and manage your investment research and opportunities").classes("text-gray-600")

        with ui.column().classes("w-full max-w-6xl mx-auto gap-8"):
            # Add new idea section
            with ui.card().classes("p-6 shadow-lg"):
                ui.label("Add New Investment Idea").classes("text-xl font-bold mb-4")
                create_investment_form()

            # Investment ideas list section
            with ui.card().classes("p-6 shadow-lg"):
                ui.label("Your Investment Ideas").classes("text-xl font-bold mb-4")
                create_ideas_list()


def create_investment_form():
    """Create form for adding new investment ideas."""

    # Form inputs
    title_input = ui.input(label="Investment Title", placeholder="e.g., Tesla Stock Analysis").classes("w-full mb-4")

    description_input = (
        ui.textarea(label="Description", placeholder="Detailed description of the investment opportunity...")
        .classes("w-full mb-4")
        .props("rows=3")
    )

    ui.label("Idea Date").classes("text-sm font-medium text-gray-700 mb-1")
    date_input = ui.date(value=date.today().isoformat()).classes("w-full mb-4")

    status_select = ui.select(
        label="Status", options=[status.value for status in InvestmentStatus], value=InvestmentStatus.RESEARCHING.value
    ).classes("w-full mb-4")

    notes_input = (
        ui.textarea(label="Additional Notes", placeholder="Research notes, analysis, thoughts...")
        .classes("w-full mb-4")
        .props("rows=4")
    )

    async def save_idea():
        """Save the new investment idea."""
        try:
            if not title_input.value or not title_input.value.strip():
                ui.notify("Please enter a title for the investment idea", type="negative")
                return

            idea_data = InvestmentIdeaCreate(
                title=title_input.value.strip(),
                description=description_input.value or "",
                idea_date=date.fromisoformat(date_input.value) if date_input.value else date.today(),
                status=InvestmentStatus(status_select.value),
                notes=notes_input.value or "",
            )

            InvestmentService.create_investment_idea(idea_data)
            ui.notify("Investment idea saved successfully!", type="positive")

            # Clear form
            title_input.set_value("")
            description_input.set_value("")
            date_input.set_value(date.today().isoformat())
            status_select.set_value(InvestmentStatus.RESEARCHING.value)
            notes_input.set_value("")

            # Refresh page to show new idea
            ui.navigate.reload()

        except Exception as e:
            logger.error(f"Error saving investment idea: {e}")
            ui.notify(f"Error saving investment idea: {str(e)}", type="negative")

    # Action buttons
    with ui.row().classes("gap-2 justify-end mt-4"):
        ui.button("Save Idea", on_click=save_idea).classes(
            "bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
        )


def create_ideas_list():
    """Create list view of all investment ideas."""

    try:
        ideas = InvestmentService.get_all_investment_ideas()

        # Filter controls
        current_filter = ui.select(
            label="Filter by Status", options=["All"] + [status.value for status in InvestmentStatus], value="All"
        ).classes("w-48 mb-4")

        def apply_filter():
            """Apply status filter and refresh display."""
            try:
                if current_filter.value == "All":
                    filtered_ideas = InvestmentService.get_all_investment_ideas()
                else:
                    status = InvestmentStatus(current_filter.value)
                    filtered_ideas = InvestmentService.get_ideas_by_status(status)

                # Clear existing ideas display
                ideas_container.clear()

                with ideas_container:
                    ui.label(f"Showing {len(filtered_ideas)} ideas").classes("text-gray-600 mb-4")

                    if not filtered_ideas:
                        display_empty_state()
                    else:
                        for idea in filtered_ideas:
                            create_idea_card(idea)
            except Exception as e:
                logger.error(f"Error applying filter: {e}")
                ui.notify(f"Error filtering ideas: {str(e)}", type="negative")

        current_filter.on("update:model-value", lambda: apply_filter())

        # Ideas container
        ideas_container = ui.column().classes("w-full")

        # Initial display
        ui.label(f"Showing {len(ideas)} ideas").classes("text-gray-600 mb-4")

        if not ideas:
            display_empty_state()
        else:
            for idea in ideas:
                create_idea_card(idea)

    except Exception as e:
        logger.error(f"Error loading ideas: {e}")
        ui.notify(f"Error loading investment ideas: {str(e)}", type="negative")


def display_empty_state():
    """Display empty state when no ideas exist."""
    with ui.card().classes("p-8 text-center"):
        ui.icon("lightbulb", size="3rem").classes("text-gray-400 mb-4")
        ui.label("No investment ideas found").classes("text-xl text-gray-600 mb-2")
        ui.label("Start by adding your first investment idea above").classes("text-gray-500")


def create_idea_card(idea: InvestmentIdeaRead):
    """Create a card component for displaying an investment idea."""

    status_colors = {
        InvestmentStatus.RESEARCHING: "bg-blue-100 text-blue-800",
        InvestmentStatus.WATCHLIST: "bg-yellow-100 text-yellow-800",
        InvestmentStatus.INVESTED: "bg-green-100 text-green-800",
        InvestmentStatus.REJECTED: "bg-red-100 text-red-800",
    }

    with ui.card().classes("p-6 mb-4 shadow-lg hover:shadow-xl transition-shadow"):
        # Header with title and status
        with ui.row().classes("justify-between items-start mb-4"):
            ui.label(idea.title).classes("text-xl font-bold text-gray-800")
            ui.label(idea.status.value).classes(
                f"px-3 py-1 rounded-full text-sm font-medium {status_colors.get(idea.status, 'bg-gray-100 text-gray-800')}"
            )

        # Idea date
        ui.label(f"Date: {idea.idea_date.strftime('%B %d, %Y')}").classes("text-sm text-gray-600 mb-2")

        # Description
        if idea.description:
            ui.label(idea.description).classes("text-gray-700 mb-3 leading-relaxed")

        # Notes
        if idea.notes:
            with ui.expansion("Additional Notes", icon="notes").classes("mb-4"):
                ui.label(idea.notes).classes("text-gray-600 whitespace-pre-wrap")

        # Action buttons
        with ui.row().classes("gap-2 justify-end"):
            ui.button("Edit", on_click=lambda e, idea_id=idea.id: show_edit_dialog(idea_id)).classes(
                "bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            ).props("outline")

            ui.button("Delete", on_click=lambda e, idea_id=idea.id: show_delete_dialog(idea_id)).classes(
                "bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            ).props("outline")


async def show_edit_dialog(idea_id: int):
    """Show dialog for editing an investment idea."""
    try:
        idea = InvestmentService.get_investment_idea_by_id(idea_id)
        if idea is None:
            ui.notify("Investment idea not found", type="negative")
            return

        with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
            ui.label("Edit Investment Idea").classes("text-xl font-bold mb-4")

            title_input = ui.input("Title", value=idea.title).classes("w-full mb-4")
            description_input = (
                ui.textarea("Description", value=idea.description).classes("w-full mb-4").props("rows=3")
            )
            ui.label("Idea Date").classes("text-sm font-medium text-gray-700 mb-1")
            date_input = ui.date(value=idea.idea_date.isoformat()).classes("w-full mb-4")
            ui.label("Status").classes("text-sm font-medium text-gray-700 mb-1")
            status_select = ui.select(
                options=[status.value for status in InvestmentStatus], value=idea.status.value
            ).classes("w-full mb-4")
            notes_input = ui.textarea("Notes", value=idea.notes).classes("w-full mb-4").props("rows=4")

            async def save_changes():
                try:
                    if not title_input.value or not title_input.value.strip():
                        ui.notify("Please enter a title", type="negative")
                        return

                    update_data = InvestmentIdeaUpdate(
                        title=title_input.value.strip(),
                        description=description_input.value or "",
                        idea_date=date.fromisoformat(date_input.value) if date_input.value else idea.idea_date,
                        status=InvestmentStatus(status_select.value),
                        notes=notes_input.value or "",
                    )

                    result = InvestmentService.update_investment_idea(idea_id, update_data)
                    if result:
                        ui.notify("Investment idea updated successfully!", type="positive")
                        dialog.close()
                        ui.navigate.reload()
                    else:
                        ui.notify("Failed to update investment idea", type="negative")
                except Exception as e:
                    logger.error(f"Error updating investment idea: {e}")
                    ui.notify(f"Error updating idea: {str(e)}", type="negative")

            with ui.row().classes("gap-2 justify-end mt-4"):
                ui.button("Cancel", on_click=dialog.close).props("outline")
                ui.button("Save Changes", on_click=save_changes).classes("bg-blue-500 text-white")

        await dialog
    except Exception as e:
        logger.error(f"Error showing edit dialog: {e}")
        ui.notify(f"Error opening edit dialog: {str(e)}", type="negative")


async def show_delete_dialog(idea_id: int):
    """Show confirmation dialog for deleting an investment idea."""
    try:
        idea = InvestmentService.get_investment_idea_by_id(idea_id)
        if idea is None:
            ui.notify("Investment idea not found", type="negative")
            return

        with ui.dialog() as dialog, ui.card().classes("w-80 p-6 text-center"):
            ui.icon("warning", size="3rem").classes("text-red-500 mb-4")
            ui.label("Delete Investment Idea").classes("text-xl font-bold mb-2")
            ui.label(f'Are you sure you want to delete "{idea.title}"?').classes("text-gray-600 mb-4")
            ui.label("This action cannot be undone.").classes("text-sm text-gray-500 mb-6")

            async def confirm_delete():
                try:
                    if InvestmentService.delete_investment_idea(idea_id):
                        ui.notify("Investment idea deleted successfully", type="warning")
                        dialog.close()
                        ui.navigate.reload()
                    else:
                        ui.notify("Failed to delete investment idea", type="negative")
                except Exception as e:
                    logger.error(f"Error deleting investment idea: {e}")
                    ui.notify(f"Error deleting idea: {str(e)}", type="negative")

            with ui.row().classes("gap-2 justify-center"):
                ui.button("Cancel", on_click=dialog.close).props("outline")
                ui.button("Delete", on_click=confirm_delete).classes("bg-red-500 text-white")

        await dialog
    except Exception as e:
        logger.error(f"Error showing delete dialog: {e}")
        ui.notify(f"Error opening delete dialog: {str(e)}", type="negative")
