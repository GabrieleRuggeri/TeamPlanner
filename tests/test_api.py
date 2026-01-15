"""API tests for TeamPlanner."""

import httpx
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.db import get_session
from app.main import app

pytestmark = pytest.mark.anyio


def _build_test_engine():
    """Create an in-memory SQLite engine for tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


async def test_user_lifecycle() -> None:
    """Ensure users can be created and listed."""

    engine = _build_test_engine()
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/users", json={"name": "Alex Doe", "email": "alex@example.com"}
            )
            assert response.status_code == 201

            list_response = await client.get("/api/users")
            assert list_response.status_code == 200
            users = list_response.json()
            assert len(users) == 1
            assert users[0]["email"] == "alex@example.com"
    finally:
        app.dependency_overrides.clear()


async def test_schedule_update_and_fetch() -> None:
    """Ensure schedule updates persist and can be queried."""

    engine = _build_test_engine()
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            create_user = await client.post(
                "/api/users", json={"name": "Sam Lee", "email": "sam@example.com"}
            )
            user_id = create_user.json()["id"]

            payload = {"user_id": user_id, "day": "2024-05-20", "status": "smart"}
            update_response = await client.put("/api/schedule", json=payload)
            assert update_response.status_code == 200

            schedule_response = await client.get(
                "/api/schedule?start=2024-05-20&end=2024-05-21"
            )
            assert schedule_response.status_code == 200
            entries = schedule_response.json()
            assert len(entries) == 1
            assert entries[0]["status"] == "smart"

            clear_payload = {
                "user_id": user_id,
                "day": "2024-05-20",
                "status": "office",
            }
            clear_response = await client.put("/api/schedule", json=clear_payload)
            assert clear_response.status_code == 200
            assert clear_response.json() == []

            empty_response = await client.get(
                "/api/schedule?start=2024-05-20&end=2024-05-20"
            )
            assert empty_response.status_code == 200
            assert empty_response.json() == []
    finally:
        app.dependency_overrides.clear()
