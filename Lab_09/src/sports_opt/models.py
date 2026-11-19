"""Моделі даних предметної області «Облік спортивних результатів»."""

from dataclasses import dataclass


@dataclass(slots=True)
class Sport:
    """Модель виду спорту."""
    id: int
    name: str
    unit: str
    is_lower_better: bool = False


@dataclass(slots=True)
class Athlete:
    """Модель спортсмена."""
    id: int
    name: str
    country: str = "Україна"
    age: int = 20


@dataclass(slots=True)
class SportResult:
    """Модель результату спортивного виступу."""
    id: int
    athlete_id: int
    athlete_name: str
    sport_id: int
    sport_name: str
    score: float
    category: str
    competition_name: str = "Чемпіонат"
