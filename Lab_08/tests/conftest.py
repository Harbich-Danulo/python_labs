"""Фікстури pytest для тестування FastAPI застосунку та асинхронного клієнта."""

from collections.abc import AsyncGenerator, Generator
from typing import Any
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sports_api.api import app
from sports_api.database import get_session
from sports_api.models import Athlete, Base, Result, Sport
from sports_api.services import SportsService


@pytest.fixture(scope="function")
def test_engine() -> Generator[Engine, None, None]:
    """Створює окремий ізольований Engine у пам'яті з підтримкою багатопоточності для FastAPI."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine: Engine) -> Generator[Session, None, None]:
    """Створює ізольовану сесію бази даних."""
    session_factory = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_engine: Engine) -> Generator[TestClient, None, None]:
    """Створює TestClient для синхронних тестів із підміною dependency get_session."""
    session_factory = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

    def _override_get_session() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(test_engine: Engine) -> AsyncGenerator[AsyncClient, None]:
    """Створює асинхронний AsyncClient із ASGITransport для тестування coroutine."""
    session_factory = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

    def _override_get_session() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed_data(test_session: Session) -> dict[str, Any]:
    """Заповнює тестову базу еталонними даними."""
    service = SportsService(test_session)
    s1 = service.register_sport("Біг на 100м", "сек", is_lower_better=True)
    s2 = service.register_sport("Стрибки у довжину", "м", is_lower_better=False)

    a1 = service.register_athlete("Данило Гарбіч", "Україна", 21)
    a2 = service.register_athlete("Олександр Зінченко", "Україна", 27)

    r1 = service.record_result(a1.id, s1.id, 10.35, "Фінал", "Меморіал")
    r2 = service.record_result(a2.id, s1.id, 11.20, "Дорослі", "Кубок")
    r3 = service.record_result(a1.id, s2.id, 7.85, "Дорослі", "Універсіада")

    return {
        "sports": [s1, s2],
        "athletes": [a1, a2],
        "results": [r1, r2, r3],
    }
