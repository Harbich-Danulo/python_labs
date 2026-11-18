"""Інтеграційні тести для сервісного шару, транзакцій (ACID) та DB-API."""

import pytest
from sqlalchemy.orm import Session
from sports_db.database import get_engine, get_session_factory, session_scope
from sports_db.db_api import (
    execute_parameterized_query,
    find_results_by_sport_dbapi,
    get_sport_statistics_dbapi,
)
from sports_db.models import Base
from sports_db.services import SportsService, ValidationError


def test_service_sport_registration(session: Session) -> None:
    service = SportsService(session)
    sport = service.register_sport("Бокс", "раунди")
    assert sport.id is not None
    assert sport.name == "Бокс"

    with pytest.raises(ValidationError, match="вже зареєстровано"):
        service.register_sport("Бокс", "раунди")

    with pytest.raises(ValidationError, match="не може бути порожньою"):
        service.register_sport("   ", "м")


def test_service_athlete_registration(session: Session) -> None:
    service = SportsService(session)
    athlete = service.register_athlete("Віталій", "Україна", 30)
    assert athlete.id is not None

    with pytest.raises(ValidationError, match="Некоректний вік"):
        service.register_athlete("Малюк", "Україна", 2)

    with pytest.raises(ValidationError, match="не може бути порожнім"):
        service.register_athlete("   ", "Україна", 25)


def test_service_record_result_validation(session: Session) -> None:
    service = SportsService(session)
    sport = service.register_sport("Біг", "сек", is_lower_better=True)
    athlete = service.register_athlete("Сергій", "Україна", 22)

    # Негативний результат
    with pytest.raises(ValidationError, match="від'ємним"):
        service.record_result(athlete.id, sport.id, -10.0, "Дорослі")

    # Неіснуючий спортсмен
    with pytest.raises(ValidationError, match="Спортсмена з ID 999 не знайдено"):
        service.record_result(999, sport.id, 10.0, "Дорослі")

    # Неіснуючий спорт
    with pytest.raises(ValidationError, match="Вид спорту з ID 888 не знайдено"):
        service.record_result(athlete.id, 888, 10.0, "Дорослі")

    # Успішний запис
    res = service.record_result(athlete.id, sport.id, 10.5, "Дорослі", "Чемпіонат")
    assert res.id is not None
    assert res.score == 10.5


def test_service_best_result_and_average(populated_session: Session) -> None:
    service = SportsService(populated_session)
    s_sprint = service.sports_repo.get_by_name("Біг на 100м")
    assert s_sprint is not None

    # Для бігу менше краще: серед 10.5 та 11.2 найкращим є 10.5
    best_sprint = service.get_best_result(s_sprint.id)
    assert best_sprint is not None
    assert best_sprint.score == 10.5

    # Середнє для бігу: (10.5 + 11.2) / 2 = 10.85
    avg_sprint = service.get_average_score(s_sprint.id)
    assert avg_sprint == 10.85

    # Для стрибків більше краще
    s_jump = service.sports_repo.get_by_name("Стрибки у висоту")
    assert s_jump is not None
    best_jump = service.get_best_result(s_jump.id)
    assert best_jump is not None
    assert best_jump.score == 2.15


def test_service_ranking(populated_session: Session) -> None:
    service = SportsService(populated_session)
    s_sprint = service.sports_repo.get_by_name("Біг на 100м")
    assert s_sprint is not None

    ranking = service.build_ranking(s_sprint.id)
    assert len(ranking) == 2
    assert ranking[0]["rank"] == 1
    assert ranking[0]["athlete_name"] == "Данило Гарбіч"
    assert ranking[0]["score"] == 10.5
    assert ranking[1]["rank"] == 2
    assert ranking[1]["athlete_name"] == "Олександр Зінченко"
    assert ranking[1]["score"] == 11.2


def test_transactional_bulk_insert_success(session: Session) -> None:
    service = SportsService(session)
    sport = service.register_sport("Тріатлон", "хв")
    athlete = service.register_athlete("Іван", "Україна", 24)

    batch = [
        {"athlete_id": athlete.id, "sport_id": sport.id, "score": 120.0, "category": "Еліта"},
        {"athlete_id": athlete.id, "sport_id": sport.id, "score": 115.5, "category": "Еліта"},
    ]
    results = service.bulk_register_results_transactional(batch)
    assert len(results) == 2
    assert len(service.results_repo.list_all()) == 2


def test_transactional_bulk_insert_rollback_atomicity(session: Session) -> None:
    """Перевірка принципу Atomicity: якщо один запис падає, rollback скасовує всі записи."""
    service = SportsService(session)
    sport = service.register_sport("Марафон", "хв")
    athlete = service.register_athlete("Олег", "Україна", 30)

    # Перший запис валідний, другий - з від'ємним результатом
    batch = [
        {"athlete_id": athlete.id, "sport_id": sport.id, "score": 130.0, "category": "Еліта"},
        {"athlete_id": athlete.id, "sport_id": sport.id, "score": -10.0, "category": "Помилка"},
    ]

    with pytest.raises(ValidationError, match="від'ємний результат"):
        service.bulk_register_results_transactional(batch)

    # Переконуємось, що ЖОДЕН запис з партії не потрапив у БД
    assert len(service.results_repo.list_all()) == 0


def test_dbapi_queries(temp_db_file: str) -> None:
    """Тестування прямих запитів DB-API та захисту від SQL-ін'єкцій."""
    # Заповнюємо тестову БД через сесію
    engine = get_engine(f"sqlite:///{temp_db_file}")
    factory = get_session_factory(engine)
    with factory() as sess:
        service = SportsService(sess)
        s = service.register_sport("Спринт", "сек", is_lower_better=True)
        a = service.register_athlete("Тарас", "Україна", 23)
        service.record_result(a.id, s.id, 10.2, "Дорослі", "Кубок")
        service.record_result(a.id, s.id, 10.4, "Дорослі", "Фінал")
    engine.dispose()

    # DB-API пошук
    res_list = find_results_by_sport_dbapi(temp_db_file, "Спринт")
    assert len(res_list) == 2
    assert res_list[0]["athlete_name"] == "Тарас"
    assert res_list[0]["score"] == 10.2

    # DB-API статистика
    stats = get_sport_statistics_dbapi(temp_db_file, "Спринт")
    assert stats is not None
    assert stats["total_results"] == 2
    assert stats["avg_score"] == 10.3
    assert stats["min_score"] == 10.2
    assert stats["max_score"] == 10.4

    # Неіснуючий спорт
    assert get_sport_statistics_dbapi(temp_db_file, "Невідомий") is None

    # Прямий параметризований запит
    raw = execute_parameterized_query(
        temp_db_file, "SELECT COUNT(*) FROM sports WHERE name = ?", ("Спринт",)
    )
    assert raw[0][0] == 1


def test_session_scope_commit_and_rollback() -> None:
    engine = get_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = get_session_factory(engine)

    # Успішний commit через контекстний менеджер
    with session_scope(factory) as sess:
        service = SportsService(sess)
        service.sports_repo.create("Велоспорт", "км/год")

    with factory() as sess:
        service = SportsService(sess)
        assert service.sports_repo.get_by_name("Велоспорт") is not None

    # Rollback при помилці
    with pytest.raises(RuntimeError):
        with session_scope(factory) as sess:
            service = SportsService(sess)
            service.sports_repo.create("Теніс", "сети")
            raise RuntimeError("Симуляція збою")

    with factory() as sess:
        service = SportsService(sess)
        assert service.sports_repo.get_by_name("Теніс") is None
