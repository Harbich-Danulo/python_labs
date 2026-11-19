"""Тестування запуску та заповнення початкових даних (main.py)."""

from unittest.mock import patch
from sports_api.main import seed_initial_data


def test_seed_initial_data() -> None:
    # Перевіряємо заповнення початкових даних
    seed_initial_data()
    # Повторний запуск не викликає помилок дублювання
    seed_initial_data()
