from app.database import create_tables
import app.investment_ui


def startup() -> None:
    # this function is called before the first request
    create_tables()
    app.investment_ui.create()
