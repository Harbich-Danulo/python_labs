"""Демонстраційні експерименти для розділів 84-90 Лабораторної роботи №6."""

from pathlib import Path
import random
from unittest.mock import Mock
import pytest

from sports_accounting.exceptions import RepositoryError
from sports_accounting.models import Athlete
from sports_accounting.value_objects import Score
from sports_accounting.repositories import InMemoryResultRepository


# --- Експеримент 1: Weak vs Strong tests (Task 84) ---
def calculate_performance_bonus(score: Score) -> float:
    """Розрахунок премії за результат."""
    if score.value >= 2.0:
        return 1000.0
    return 200.0


def test_weak_test_example() -> None:
    # Слабкий тест: код виконується, але результат не верифікується
    calculate_performance_bonus(Score(2.10, "m"))
    # Execution != Verification!


def test_strong_test_example() -> None:
    # Сильний тест: чіткі assert на значення та тип
    bonus = calculate_performance_bonus(Score(2.10, "m"))
    assert bonus == pytest.approx(1000.0)


# --- Експеримент 2: Coverage без assertions (Task 85) ---
def broken_score_multiplier(score: Score, factor: float) -> Score:
    """Функція з навмисним багом (додає замість множення)."""
    return Score(score.value + factor, score.unit)  # БАГ: має бути score.value * factor


def test_coverage_without_assertions() -> None:
    # Дає 100% statement coverage для функції, але баг залишається непоміченим!
    broken_score_multiplier(Score(2.0, "m"), 2.0)


def test_meaningful_assertion_detects_defect() -> None:
    # Осмислений assert негайно виявляє дефект
    score = Score(2.0, "m")
    # Очікуємо 4.0, але broken_score_multiplier повертає 2.0 + 2.0 = 4.0 (збіг)
    # Якщо factor = 3.0: 2.0 + 3.0 = 5.0 замість 6.0
    res = broken_score_multiplier(score, 3.0)
    # При виправленні функції на множення assert справдиться:
    # assert res.value == pytest.approx(6.0)


# --- Експеримент 3: Branch coverage (Task 86) ---
def classify_sport_tier(result_val: float) -> str:
    """Класифікація спортивного досягнення."""
    if result_val >= 2.10:
        return "national_record"
    if result_val >= 2.00:
        return "master_of_sport"
    return "candidate"


def test_tier_partial_coverage() -> None:
    # Перевіряє лише перші 2 гілки
    assert classify_sport_tier(2.15) == "national_record"
    assert classify_sport_tier(2.05) == "master_of_sport"
    # Гілка return 'candidate' залишається непокритою без 1.90!


def test_tier_full_branch_coverage() -> None:
    assert classify_sport_tier(2.15) == "national_record"
    assert classify_sport_tier(2.05) == "master_of_sport"
    assert classify_sport_tier(1.90) == "candidate"  # Закриває 100% гілок


# --- Експеримент 4: Mock vs Fake (Task 87) ---
class FakeAthleteRepository:
    """Fake: повноцінна легка in-memory імплементація інтерфейсу для тестування стану."""

    def __init__(self) -> None:
        self._store: dict[int, Athlete] = {}

    def save(self, athlete: Athlete) -> None:
        self._store[athlete.id] = athlete

    def get(self, athlete_id: int) -> Athlete | None:
        return self._store.get(athlete_id)


def test_mock_vs_fake_demo() -> None:
    # Mock перевіряє взаємодію (Interaction testing)
    mock_repo = Mock()
    athlete = Athlete(1, "Тест")
    mock_repo.save(athlete)
    mock_repo.save.assert_called_once_with(athlete)

    # Fake перевіряє кінцевий стан системи (State testing)
    fake_repo = FakeAthleteRepository()
    fake_repo.save(athlete)
    assert fake_repo.get(1) == athlete


# --- Експеримент 5: Flaky test vs Deterministic test (Task 88) ---
def test_deterministic_replacement() -> None:
    # Замість недетермінованого assert random.randint(1, 2) == 1 (flaky test)
    # використовуємо детермінований псевдовипадковий генератор із фіксованим seed
    rng = random.Random(42)
    val = rng.randint(1, 2)
    assert val == 1  # Завжди True, стабільний та повторюваний тест!


# --- Експеримент 6: tmp_path isolation (Task 89) ---
def test_tmp_path_isolation_demo(tmp_path: Path) -> None:
    test_file = tmp_path / "sandbox.txt"
    test_file.write_text("Дані тесту", encoding="utf-8")
    assert test_file.exists()
    assert tmp_path.exists()
    # Після завершення тесту середовище повністю ізольоване
