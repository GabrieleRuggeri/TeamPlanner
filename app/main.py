"""FastAPI application entrypoint for TeamPlanner."""

from datetime import date
import logging
from typing import Iterable

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session
import uvicorn

from app import crud
from app.config import get_settings
from app.db import get_session, init_db
from app.models import ScheduleEntry, User
from app.schemas import ScheduleResponse, ScheduleUpdate, UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize application resources."""

    init_db()
    logger.info("Database initialized")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a health status for monitoring.

    Returns:
        Dictionary indicating application status.
    """

    return {"status": "ok"}


@app.get("/")
def root() -> RedirectResponse:
    """Redirect to the user management page."""

    return RedirectResponse(url="/static/index.html")


@app.get("/api/users", response_model=list[User])
def read_users(session: Session = Depends(get_session)) -> list[User]:
    """List all users.

    Args:
        session: Database session dependency.

    Returns:
        List of users.
    """

    return crud.list_users(session)


@app.post("/api/users", response_model=User, status_code=201)
def create_user(
    payload: UserCreate, session: Session = Depends(get_session)
) -> User:
    """Create a new user.

    Args:
        payload: User creation payload.
        session: Database session dependency.

    Returns:
        Newly created user.
    """

    if not payload.name.strip() or not payload.email.strip():
        raise HTTPException(status_code=400, detail="Name and email are required")
    return crud.create_user(session, payload.name.strip(), payload.email.strip())


@app.get("/api/schedule", response_model=list[ScheduleResponse])
def read_schedule(
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    session: Session = Depends(get_session),
) -> list[ScheduleResponse]:
    """Return schedule entries in a date range.

    Args:
        start: Start date.
        end: End date.
        session: Database session dependency.

    Returns:
        List of schedule entries.
    """

    if start > end:
        raise HTTPException(status_code=400, detail="Start date must precede end")
    entries = crud.get_schedule_entries(session, start, end)
    return [ScheduleResponse(**entry.dict()) for entry in entries]


@app.put("/api/schedule", response_model=list[ScheduleResponse])
def update_schedule(
    payload: ScheduleUpdate, session: Session = Depends(get_session)
) -> list[ScheduleResponse]:
    """Update a user's schedule for a day.

    Args:
        payload: Schedule update payload.
        session: Database session dependency.

    Returns:
        List containing the updated schedule entry, or empty if removed.
    """

    entries: Iterable[ScheduleEntry] = crud.upsert_schedule_entry(
        session, payload.user_id, payload.day, payload.status
    )
    return [ScheduleResponse(**entry.dict()) for entry in entries]


app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "local",
    )
