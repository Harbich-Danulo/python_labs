"""Додаткові тести покриття для Score та винятків."""

import pytest

from sports_accounting.exceptions import RecordValidationError
from sports_accounting.models import Athlete, Competition, Sport
from sports_accounting.value_objects import Score


def test_score_not_implemented_operations() -> None:
    score = Score(2.10, "m")
    invalid_other: object = 10
    # Перевірка операцій з не-Score об'єктами (повертає NotImplemented, що викликає TypeError)
    with pytest.raises(TypeError):
        _ = score + invalid_other
    with pytest.raises(TypeError):
        _ = score - invalid_other
    with pytest.raises(TypeError):
        _ = score < invalid_other
    with pytest.raises(TypeError):
        _ = score > invalid_other


def test_record_validation_error_str_formatting() -> None:
    err1 = RecordValidationError("Помилка")
    assert str(err1) == "Помилка"

    err2 = RecordValidationError("Помилка", line_number=5, field="athlete", raw_value="X")
    s = str(err2)
    assert "рядок 5" in s
    assert "поле 'athlete'" in s
    assert "значення='X'" in s


def test_sport_and_competition_empty_validations() -> None:
    with pytest.raises(ValueError, match="Назва виду спорту не може бути порожньою"):
        Sport(id=1, name="   ", unit="m")

    with pytest.raises(ValueError, match="ID змагання має бути додатнім"):
        Competition(id=0, name="Олімпіада", location="Париж", year=2024)

    with pytest.raises(ValueError, match="Назва змагання не може бути порожньою"):
        Competition(id=1, name="   ", location="Париж", year=2024)
