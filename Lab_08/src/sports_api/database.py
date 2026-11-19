"""Керування базою даних, з'єднаннями та FastAPI-залежностями для SQLAlchemy."""

import os
from collections.abc import Generator
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sports_api.models import Base

DB_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sports.db"))
DEFAULT_DB_URL: str = f"sqlite:///{DB_PATH}"


def get_engine(db_url: str = DEFAULT_DB_URL, echo: bool = False) -> Engine:
    """Створює Engine з увімкненою посилальною цілісністю (foreign_keys=ON) для SQLite."""
    engine = create_engine(db_url, echo=echo)
    if db_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    return engine


engine: Engine = get_engine(DEFAULT_DB_URL)
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)


def init_db(target_engine: Engine = engine) -> None:
    """Створює каталог для бази та ініціалізує схему таблиць."""
    db_file = str(target_engine.url).replace("sqlite:///", "")
    if db_file and not db_file.startswith(":memory:"):
        os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)
    Base.metadata.create_all(bind=target_engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI Dependency: надає сесію бази даних із гарантованим закриттям."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
