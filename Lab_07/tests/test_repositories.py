"""Інтеграційні тести для репозиторіїв (SportRepository, AthleteRepository, ResultRepository)."""

from sqlalchemy.orm import Session
from sports_db.repositories import AthleteRepository, ResultRepository, SportRepository


def test_sport_repository_crud(session: Session) -> None:
    repo = SportRepository(session)

    # 1. Create
    sport = repo.create("Плавання 100м", "сек", is_lower_better=True)
    assert sport.id is not None
    assert sport.name == "Плавання 100м"
    assert sport.is_lower_better is True

    # 2. Read by ID and Name
    found = repo.get_by_id(sport.id)
    assert found is not None
    assert found.name == "Плавання 100м"

    found_by_name = repo.get_by_name("Плавання 100м")
    assert found_by_name is not None
    assert found_by_name.id == sport.id

    # 3. List
    sports = repo.list_all()
    assert len(sports) == 1
    assert sports[0].name == "Плавання 100м"

    # 4. Update
    updated = repo.update(sport.id, unit="хв:сек")
    assert updated is not None
    assert updated.unit == "хв:сек"

    # 5. Delete
    deleted = repo.delete(sport.id)
    assert deleted is True
    assert repo.get_by_id(sport.id) is None
    assert repo.delete(999) is False


def test_athlete_repository_crud(session: Session) -> None:
    repo = AthleteRepository(session)

    # 1. Create
    athlete = repo.create("Данило Гарбіч", "Україна", 21)
    assert athlete.id is not None
    assert athlete.name == "Данило Гарбіч"
    assert athlete.age == 21

    # 2. Read
    found = repo.get_by_id(athlete.id)
    assert found is not None
    assert found.name == "Данило Гарбіч"

    by_name = repo.get_by_name("Данило Гарбіч")
    assert len(by_name) == 1

    # 3. List
    athletes = repo.list_all()
    assert len(athletes) == 1

    # 4. Update
    updated = repo.update(athlete.id, age=22, country="Польща")
    assert updated is not None
    assert updated.age == 22
    assert updated.country == "Польща"

    # 5. Delete
    deleted = repo.delete(athlete.id)
    assert deleted is True
    assert repo.get_by_id(athlete.id) is None
    assert repo.delete(9999) is False


def test_result_repository_crud_and_filters(session: Session) -> None:
    s_repo = SportRepository(session)
    a_repo = AthleteRepository(session)
    r_repo = ResultRepository(session)

    sport = s_repo.create("Біг 200м", "сек", is_lower_better=True)
    athlete1 = a_repo.create("Атлет 1", "Україна", 20)
    athlete2 = a_repo.create("Атлет 2", "Україна", 25)

    # Create
    r1 = r_repo.create(athlete1.id, sport.id, 21.4, "Дорослі", "Кубок")
    r2 = r_repo.create(athlete2.id, sport.id, 22.1, "Юніори", "Кубок")
    assert r1.id is not None
    assert r2.id is not None

    # Read
    found = r_repo.get_by_id(r1.id)
    assert found is not None
    assert found.score == 21.4

    # List & Filters
    all_res = r_repo.list_all()
    assert len(all_res) == 2

    by_sport = r_repo.filter_by_sport(sport.id)
    assert len(by_sport) == 2

    by_athlete = r_repo.filter_by_athlete(athlete1.id)
    assert len(by_athlete) == 1
    assert by_athlete[0].athlete_id == athlete1.id

    by_cat = r_repo.filter_by_category("Юніори")
    assert len(by_cat) == 1
    assert by_cat[0].athlete_id == athlete2.id

    # Update
    updated = r_repo.update(r1.id, score=21.05)
    assert updated is not None
    assert updated.score == 21.05

    # Delete
    deleted = r_repo.delete(r1.id)
    assert deleted is True
    assert r_repo.get_by_id(r1.id) is None
    assert r_repo.delete(9999) is False


def test_cascade_delete(session: Session) -> None:
    s_repo = SportRepository(session)
    a_repo = AthleteRepository(session)
    r_repo = ResultRepository(session)

    sport = s_repo.create("Дзюдо", "бали")
    athlete = a_repo.create("Іван", "Україна", 24)
    r = r_repo.create(athlete.id, sport.id, 100.0, "Майстри")

    # Перевіряємо каскадне видалення при видаленні athlete
    a_repo.delete(athlete.id)
    assert r_repo.get_by_id(r.id) is None
