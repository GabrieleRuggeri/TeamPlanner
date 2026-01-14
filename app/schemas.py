"""Pydantic schemas for API payloads."""

from datetime import date

from sqlmodel import SQLModel

from app.models import ScheduleStatus


class UserCreate(SQLModel):
    """Payload for creating a user."""

    name: str
    email: str


class ScheduleUpdate(SQLModel):
    """Payload for updating a schedule entry."""

    user_id: int
    day: date
    status: ScheduleStatus


class ScheduleResponse(SQLModel):
    """Serialized schedule entry for API responses."""

    user_id: int
    day: date
    status: ScheduleStatus
