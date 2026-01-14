"""CRUD helpers for TeamPlanner."""

from datetime import date
import logging
from typing import Iterable

from sqlmodel import Session, select

from app.models import ScheduleEntry, ScheduleStatus, User

logger = logging.getLogger(__name__)


def list_users(session: Session) -> list[User]:
    """Return all users ordered by name.

    Args:
        session: Active database session.

    Returns:
        List of users.
    """

    statement = select(User).order_by(User.name)
    return list(session.exec(statement))


def create_user(session: Session, name: str, email: str) -> User:
    """Create and persist a new user.

    Args:
        session: Active database session.
        name: User full name.
        email: User email address.

    Returns:
        Persisted User instance.
    """

    user = User(name=name, email=email)
    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info("Created user %s", user.email)
    return user


def get_schedule_entries(
    session: Session, start_day: date, end_day: date
) -> list[ScheduleEntry]:
    """Fetch schedule entries in the requested date range.

    Args:
        session: Active database session.
        start_day: Start date (inclusive).
        end_day: End date (inclusive).

    Returns:
        List of schedule entries.
    """

    statement = (
        select(ScheduleEntry)
        .where(ScheduleEntry.day >= start_day)
        .where(ScheduleEntry.day <= end_day)
    )
    return list(session.exec(statement))


def upsert_schedule_entry(
    session: Session, user_id: int, day: date, status: ScheduleStatus
) -> Iterable[ScheduleEntry]:
    """Create, update, or delete a schedule entry.

    Args:
        session: Active database session.
        user_id: User identifier.
        day: Scheduled date.
        status: New schedule status.

    Returns:
        Iterable containing the updated entry, or empty if deleted.
    """

    statement = select(ScheduleEntry).where(
        ScheduleEntry.user_id == user_id, ScheduleEntry.day == day
    )
    existing = session.exec(statement).one_or_none()

    if status == ScheduleStatus.OFFICE:
        if existing:
            session.delete(existing)
            session.commit()
            logger.info("Cleared schedule for user %s on %s", user_id, day)
        return []

    if existing:
        existing.status = status
        session.add(existing)
        session.commit()
        session.refresh(existing)
        logger.info("Updated schedule for user %s on %s", user_id, day)
        return [existing]

    entry = ScheduleEntry(user_id=user_id, day=day, status=status)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    logger.info("Created schedule for user %s on %s", user_id, day)
    return [entry]
