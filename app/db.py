"""Database initialization and session management."""

import logging
import time
from typing import Generator

from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

logger = logging.getLogger(__name__)


def _build_engine() -> tuple[str, dict[str, object]]:
    """Build the database engine configuration.

    Returns:
        Tuple of database URL and engine keyword arguments.
    """

    settings = get_settings()
    connect_args: dict[str, object] = {}
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return settings.database_url, {"connect_args": connect_args}


DATABASE_URL, ENGINE_KWARGS = _build_engine()
engine = create_engine(DATABASE_URL, echo=False, **ENGINE_KWARGS)


def init_db(max_attempts: int = 30, delay_seconds: float = 1.0) -> None:
    """Create database tables if they do not exist.

    Args:
        max_attempts: Maximum connection attempts before failing.
        delay_seconds: Delay between attempts.
    """

    for attempt in range(1, max_attempts + 1):
        try:
            SQLModel.metadata.create_all(engine)
        except OperationalError:
            if attempt == max_attempts:
                raise
            logger.warning(
                "Database not ready (attempt %s/%s); retrying in %ss",
                attempt,
                max_attempts,
                delay_seconds,
            )
            time.sleep(delay_seconds)
            continue
        return


def get_session() -> Generator[Session, None, None]:
    """Provide a database session.

    Yields:
        SQLModel session bound to the engine.
    """

    with Session(engine) as session:
        yield session
