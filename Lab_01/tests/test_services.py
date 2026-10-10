"""Tests for sports_tracker services and models."""

from sports_tracker.models import Athlete, InvalidAthleteDataError
from sports_tracker.services import (
    add_result,
    calculate_average_result,
    calculate_statistics,
    filter_by_multiple_criteria,
    filter_by_sport,
    find_best_result,
    generate_ranking,
)


def sample_data() -> list[Athlete]:
    return [
        Athlete("Ярослава Магучіх", "Стрибки у висоту", 2.10, "Дорослі"),
        Athlete("Ірина Геращенко", "Стрибки у висоту", 2.00, "Дорослі"),
        Athlete("Юлія Левченко", "Стрибки у висоту", 1.95, "Дорослі"),
        Athlete("Михайло Романчук", "Плавання 1500м", 870.5, "Дорослі"),
    ]


def test_add_result() -> None:
    data = sample_data()
    new_athlete = Athlete("Олег Верняєв", "Гімнастика", 15.2, "Майстри")
    add_result(data, new_athlete)
    assert len(data) == 5
    assert data[-1].name == "Олег Верняєв"


def test_filter_by_sport() -> None:
    data = sample_data()
    jumpers = filter_by_sport(data, "Стрибки у висоту")
    assert len(jumpers) == 3
    assert all(a.sport == "Стрибки у висоту" for a in jumpers)


def test_find_best_result() -> None:
    data = sample_data()
    best_jumper = find_best_result(data, "Стрибки у висоту")
    assert best_jumper is not None
    assert best_jumper.name == "Ярослава Магучіх"
    assert best_jumper.result == 2.10


def test_calculate_average_result() -> None:
    data = sample_data()
    avg = calculate_average_result(data, "Стрибки у висоту")
    # (2.10 + 2.00 + 1.95) / 3 = 6.05 / 3 = 2.01666... -> rounded to 2.02
    assert avg == 2.02


def test_generate_ranking() -> None:
    data = sample_data()
    ranked = generate_ranking(data, "Стрибки у висоту")
    assert ranked[0].name == "Ярослава Магучіх"
    assert ranked[1].name == "Ірина Геращенко"
    assert ranked[2].name == "Юлія Левченко"


def test_validation() -> None:
    try:
        Athlete("", "Біг", 10.5, "Юніори")
        assert False, "Should have raised InvalidAthleteDataError"
    except InvalidAthleteDataError:
        pass


if __name__ == "__main__":
    test_add_result()
    test_filter_by_sport()
    test_find_best_result()
    test_calculate_average_result()
    test_generate_ranking()
    test_validation()
    print("All tests passed successfully!")
