"""API tests for TeamPlanner."""

from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.db import get_session
from app.main import app


def _build_test_engine():
    """Create an in-memory SQLite engine for tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_user_lifecycle() -> None:
    """Ensure users can be created and listed."""

    engine = _build_test_engine()
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    response = client.post(
        "/api/users", json={"name": "Alex Doe", "email": "alex@example.com"}
    )
    assert response.status_code == 201

    list_response = client.get("/api/users")
    assert list_response.status_code == 200
    users = list_response.json()
    assert len(users) == 1
    assert users[0]["email"] == "alex@example.com"

    app.dependency_overrides.clear()


def test_schedule_update_and_fetch() -> None:
    """Ensure schedule updates persist and can be queried."""

    engine = _build_test_engine()
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    create_user = client.post(
        "/api/users", json={"name": "Sam Lee", "email": "sam@example.com"}
    )
    user_id = create_user.json()["id"]

    payload = {"user_id": user_id, "day": "2024-05-20", "status": "smart"}
    update_response = client.put("/api/schedule", json=payload)
    assert update_response.status_code == 200

    schedule_response = client.get(
        "/api/schedule?start=2024-05-20&end=2024-05-21"
    )
    assert schedule_response.status_code == 200
    entries = schedule_response.json()
    assert len(entries) == 1
    assert entries[0]["status"] == "smart"

    clear_payload = {"user_id": user_id, "day": "2024-05-20", "status": "office"}
    clear_response = client.put("/api/schedule", json=clear_payload)
    assert clear_response.status_code == 200
    assert clear_response.json() == []

    empty_response = client.get(
        "/api/schedule?start=2024-05-20&end=2024-05-20"
    )
    assert empty_response.status_code == 200
    assert empty_response.json() == []

    app.dependency_overrides.clear()
