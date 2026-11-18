"""Конфігурація pytest та фікстури для інтеграційних тестів."""

import os
import tempfile
from typing import Generator
import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sports_db.database import get_session_factory
from sports_db.models import Athlete, Base, Result, Sport


@pytest.fixture(scope="function")
def engine() -> Generator[Engine, None, None]:
    """Створює ізольований SQLite Engine у пам'яті для кожного тесту."""
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def session(engine: Engine) -> Generator[Session, None, None]:
    """Створює сесію бази даних для тесту з автоматичним закриттям."""
    factory = get_session_factory(engine)
    db_session = factory()
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture(scope="function")
def populated_session(session: Session) -> Session:
    """Сесія із заздалегідь заповненими тестовими даними."""
    s1 = Sport(name="Біг на 100м", unit="сек", is_lower_better=True)
    s2 = Sport(name="Стрибки у висоту", unit="м", is_lower_better=False)
    session.add_all([s1, s2])
    session.flush()

    a1 = Athlete(name="Данило Гарбіч", country="Україна", age=21)
    a2 = Athlete(name="Олександр Зінченко", country="Україна", age=27)
    session.add_all([a1, a2])
    session.flush()

    r1 = Result(athlete_id=a1.id, sport_id=s1.id, score=10.5, category="Дорослі", competition_name="Кубок")
    r2 = Result(athlete_id=a2.id, sport_id=s1.id, score=11.2, category="Дорослі", competition_name="Кубок")
    r3 = Result(athlete_id=a1.id, sport_id=s2.id, score=2.15, category="Дорослі", competition_name="Чемпіонат")
    session.add_all([r1, r2, r3])
    session.commit()
    return session


@pytest.fixture(scope="function")
def temp_db_file() -> Generator[str, None, None]:
    """Створює тимчасовий файл SQLite для тестування DB-API."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    # Ініціалізуємо таблиці
    file_engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(file_engine)
    file_engine.dispose()

    yield db_path

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass
