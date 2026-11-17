"""Конфігурація тестового середовища та спільні фікстури pytest."""

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
import pytest

from sports_accounting.config import AppConfig, SportRuleConfig
from sports_accounting.models import Athlete, Competition, Result, Sport
from sports_accounting.repositories import InMemoryResultRepository
from sports_accounting.value_objects import Score


@pytest.fixture
def sample_athlete() -> Athlete:
    """Фікстура спортсмена для базових тестів."""
    return Athlete(
        id=101,
        name="Ярослава Магучіх",
        country="Україна",
        age=22,
    )


@pytest.fixture
def sample_sport_high_jump() -> Sport:
    """Фікстура виду спорту (більший бал краще)."""
    return Sport(
        id=1,
        name="Стрибки у висоту",
        unit="m",
        is_lower_better=False,
    )


@pytest.fixture
def sample_sport_swimming() -> Sport:
    """Фікстура виду спорту (менший час краще)."""
    return Sport(
        id=2,
        name="Плавання 800м",
        unit="s",
        is_lower_better=True,
    )


@pytest.fixture
def sample_competition() -> Competition:
    """Фікстура змагання."""
    return Competition(
        id=10,
        name="Олімпійські Ігри",
        location="Париж",
        year=2024,
    )


@pytest.fixture
def sample_result(
    sample_athlete: Athlete,
    sample_sport_high_jump: Sport,
    sample_competition: Competition,
) -> Result:
    """Фікстура одиночного результату."""
    return Result(
        id=1,
        athlete=sample_athlete,
        sport=sample_sport_high_jump,
        competition=sample_competition,
        score=Score(value=2.10, unit="m"),
        category="Дорослі",
        timestamp=datetime(2024, 7, 7, 18, 30),
    )


@pytest.fixture
def result_factory(
    sample_sport_high_jump: Sport,
    sample_competition: Competition,
) -> Callable[..., Result]:
    """Фабрика фікстур (Fixture factory, Task 96) для гнучкого створення результатів."""

    def _factory(
        *,
        result_id: int = 1,
        athlete_id: int = 101,
        athlete_name: str = "Атлет",
        score_value: float = 2.00,
        unit: str = "m",
        sport: Sport | None = None,
        category: str = "Дорослі",
        timestamp: datetime | None = None,
    ) -> Result:
        current_sport = sport or sample_sport_high_jump
        athlete = Athlete(id=athlete_id, name=athlete_name, country="Україна", age=24)
        return Result(
            id=result_id,
            athlete=athlete,
            sport=current_sport,
            competition=sample_competition,
            score=Score(value=score_value, unit=unit),
            category=category,
            timestamp=timestamp or datetime(2024, 8, 1, 12, 0),
        )

    return _factory


@pytest.fixture
def sample_results_list(
    result_factory: Callable[..., Result],
    sample_sport_high_jump: Sport,
) -> list[Result]:
    """Колекція результатів зі стрибків у висоту для тестування сортування та нічиїх."""
    return [
        result_factory(result_id=1, athlete_id=101, athlete_name="Ярослава Магучіх", score_value=2.10),
        result_factory(result_id=2, athlete_id=102, athlete_name="Ірина Геращенко", score_value=2.00),
        result_factory(result_id=3, athlete_id=103, athlete_name="Юлія Левченко", score_value=1.95),
        result_factory(result_id=4, athlete_id=104, athlete_name="Катерина Табашник", score_value=1.95),  # Нічия (tie)
    ]


@pytest.fixture
def sample_config(tmp_path: Path) -> AppConfig:
    """Фікстура валідної конфігурації із ізольованими шляхами tmp_path."""
    return AppConfig(
        input_path=tmp_path / "input.csv",
        output_path=tmp_path / "output.json",
        allowed_sports=("Стрибки у висоту", "Плавання 800м", "Спортивна гімнастика"),
        allowed_categories=("Дорослі", "Юніори", "Молодь", "Ветерани"),
        sport_rules={
            "Стрибки у висоту": SportRuleConfig(min_value=1.00, max_value=2.50),
            "Плавання 800м": SportRuleConfig(min_value=400.00, max_value=800.00),
            "Спортивна гімнастика": SportRuleConfig(min_value=10.00, max_value=16.50),
        },
        min_timestamp=datetime(2024, 1, 1),
        env_mode="testing",
        log_level="INFO",
    )


@pytest.fixture
def managed_repository() -> Iterator[InMemoryResultRepository]:
    """Фікстура із життєвим циклом teardown (yield) для гарантованого очищення."""
    repo = InMemoryResultRepository()
    yield repo
    # Teardown logic
    repo._items.clear()
