"""Тестування репозиторіїв та операцій persistence layer."""

from sqlalchemy.orm import Session
from sports_api.repositories import AthleteRepository, ResultRepository, SportRepository


def test_sport_repository(test_session: Session) -> None:
    repo = SportRepository(test_session)
    sport = repo.create("Плавання 100м", "сек", is_lower_better=True)
    assert sport.id is not None
    assert sport.name == "Плавання 100м"

    found = repo.get_by_id(sport.id)
    assert found is not None
    assert found.name == "Плавання 100м"

    found_name = repo.get_by_name("Плавання 100м")
    assert found_name is not None
    assert found_name.id == sport.id

    all_sports = repo.list_all()
    assert len(all_sports) == 1

    updated = repo.update(sport, unit="хв")
    assert updated.unit == "хв"

    repo.delete(sport)
    assert repo.get_by_id(sport.id) is None


def test_athlete_repository(test_session: Session) -> None:
    repo = AthleteRepository(test_session)
    athlete = repo.create("Данило Гарбіч", "Україна", 21)
    assert athlete.id is not None

    found = repo.get_by_id(athlete.id)
    assert found is not None
    assert found.name == "Данило Гарбіч"

    by_query = repo.list_all(name_query="Гарбіч", country="Україна")
    assert len(by_query) == 1

    updated = repo.update(athlete, age=22)
    assert updated.age == 22

    repo.delete(athlete)
    assert repo.get_by_id(athlete.id) is None


def test_result_repository(test_session: Session) -> None:
    s_repo = SportRepository(test_session)
    a_repo = AthleteRepository(test_session)
    r_repo = ResultRepository(test_session)

    sport = s_repo.create("Біг 60м", "сек", is_lower_better=True)
    athlete = a_repo.create("Олег", "Україна", 24)

    res = r_repo.create(athlete.id, sport.id, 6.75, "Дорослі", "Чемпіонат")
    assert res.id is not None

    found = r_repo.get_by_id(res.id)
    assert found is not None
    assert found.score == 6.75

    filtered = r_repo.filter_by_sport(sport.id, category="Дорослі", min_score=6.0, max_score=7.0)
    assert len(filtered) == 1

    updated = r_repo.update(res, score=6.70)
    assert updated.score == 6.70

    all_res = r_repo.list_all()
    assert len(all_res) == 1

    r_repo.delete(res)
    assert r_repo.get_by_id(res.id) is None
