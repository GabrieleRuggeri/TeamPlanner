"""Database models for TeamPlanner."""

from __future__ import annotations

from datetime import date
from enum import Enum

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class ScheduleStatus(str, Enum):
    """Supported schedule statuses for a day."""

    OFFICE = "office"
    SMART_WORKING = "smart"
    AWAY = "away"


class User(SQLModel, table=True):
    """Represents a team member.

    Attributes:
        id: Primary key identifier.
        name: Full name of the user.
        email: Contact email for the user.
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str


class ScheduleEntry(SQLModel, table=True):
    """Represents a scheduled day for a user.

    Attributes:
        id: Primary key identifier.
        user_id: Foreign key to the user.
        day: Calendar date for the schedule.
        status: Scheduled status for the day.
    """

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    day: date = Field(index=True)
    status: ScheduleStatus

    __table_args__ = (
        UniqueConstraint("user_id", "day", name="uq_schedule_user_day"),
        {"sqlite_autoincrement": True},
    )
