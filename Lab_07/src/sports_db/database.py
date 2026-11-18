"""Модуль налаштування підключення до бази даних та керування сесіями SQLAlchemy."""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

DEFAULT_DB_URL: str = "sqlite:///data/sports.db"


def get_engine(db_url: str = DEFAULT_DB_URL, echo: bool = False) -> Engine:
    """Створює та повертає SQLAlchemy Engine.
    
    Для SQLite вмикається перевірка зовнішніх ключів (foreign_keys=ON).
    """
    engine = create_engine(db_url, echo=echo)
    if db_url.startswith("sqlite"):
        from sqlalchemy import event

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Створює фабрику сесій SQLAlchemy з прив'язкою до зазначеного engine."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Контекстний менеджер транзакційної сесії з автоматичним commit/rollback."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
