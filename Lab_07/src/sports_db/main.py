"""Точка входу програми (CLI-демонстрація та інтерфейс користувача).

Демонструє:
1. Ініціалізацію схеми бази даних через SQLAlchemy ORM.
2. Роботу Repository Pattern (CRUD для Sport, Athlete, Result).
3. Виконання прямого параметризованого DB-API запиту (захист від SQL Injection).
4. Атомарність транзакцій (ACID Atomicity): демонстрація Commit та Rollback.
5. Обчислення аналітики: AVG(), MAX(), формування підсумкового рейтингу.
"""

import os
import sys
from typing import List
from sqlalchemy import select
from sports_db.database import get_engine, get_session_factory
from sports_db.db_api import find_results_by_sport_dbapi, get_sport_statistics_dbapi
from sports_db.models import Base, Sport
from sports_db.services import SportsService, ValidationError

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sports.db"))
DB_URL = f"sqlite:///{DB_PATH}"


def initialize_database() -> None:
    """Створює каталоги та таблиці бази даних."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    engine = get_engine(DB_URL)
    Base.metadata.create_all(engine)
    print(f"Базу даних ініціалізовано: {DB_PATH}")


def seed_sample_data(service: SportsService) -> None:
    """Заповнює базу даних демонстраційними записами."""
    print("\n--- Заповнення початкових даних ---")
    s1 = service.register_sport(name="Біг на 100м", unit="сек", is_lower_better=True)
    s2 = service.register_sport(name="Стрибки у довжину", unit="м", is_lower_better=False)
    s3 = service.register_sport(name="Плавання 50м", unit="сек", is_lower_better=True)

    a1 = service.register_athlete(name="Данило Гарбіч", country="Україна", age=21)
    a2 = service.register_athlete(name="Олександр Зінченко", country="Україна", age=27)
    a3 = service.register_athlete(name="Ярослава Магучіх", country="Україна", age=22)
    a4 = service.register_athlete(name="Михайло Романчук", country="Україна", age=28)

    service.record_result(a1.id, s1.id, 10.45, "Дорослі", "Чемпіонат України")
    service.record_result(a2.id, s1.id, 11.20, "Дорослі", "Кубок НОК")
    service.record_result(a1.id, s2.id, 7.85, "Дорослі", "Універсіада")
    service.record_result(a3.id, s2.id, 8.12, "Дорослі", "Diamond League")
    service.record_result(a4.id, s3.id, 21.80, "Дорослі", "Олімпійський відбір")
    service.record_result(a1.id, s3.id, 24.15, "Юніори", "Кубок ректора")
    print("Демонстраційні дані успішно завантажено!")


def demonstrate_acid_transaction(service: SportsService) -> None:
    """Демонстрація принципу атомарності (Atomicity) в транзакції."""
    print("\n--- Демонстрація транзакцій (ACID: Commit та Rollback) ---")
    athletes = service.athletes_repo.list_all()
    sports = service.sports_repo.list_all()
    if not athletes or not sports:
        print("Недостатньо даних для демонстрації транзакцій.")
        return

    a_id = athletes[0].id
    s_id = sports[0].id

    print("1. Спроба додати партію результатів з помилкою (один результат від'ємний: -5.0):")
    invalid_batch = [
        {"athlete_id": a_id, "sport_id": s_id, "score": 10.50, "category": "Тест 1", "competition_name": "Тест"},
        {"athlete_id": a_id, "sport_id": s_id, "score": -5.0, "category": "Некоректний", "competition_name": "Тест"},
    ]
    try:
        service.bulk_register_results_transactional(invalid_batch)
        print("Помилка: транзакція мала впасти, але виконалась!")
    except ValidationError as err:
        print(f"Отримано очікуване виключення: {err}")
        print("Транзакцію скасовано (ROLLBACK). Жоден запис з партії не додано.")

    print("\n2. Успішна транзакція (коректні дані):")
    valid_batch = [
        {"athlete_id": a_id, "sport_id": s_id, "score": 10.35, "category": "Фінал", "competition_name": "Меморіал"},
    ]
    try:
        res = service.bulk_register_results_transactional(valid_batch)
        print(f"Транзакцію успішно зафіксовано (COMMIT): додано {len(res)} запис(ів).")
    except Exception as err:
        print(f"Помилка фіксації: {err}")


def display_analytics_and_ranking(service: SportsService) -> None:
    """Виводить аналітику та сформовані рейтинги."""
    print("\n--- Аналітика та спортивні рейтинги ---")
    sports = service.sports_repo.list_all()
    for sport in sports:
        print(f"\n================ Дисципліна: {sport.name} ({sport.unit}) ================")
        best = service.get_best_result(sport.id)
        avg_score = service.get_average_score(sport.id)
        if best:
            direction = "менше краще" if sport.is_lower_better else "більше краще"
            print(f"Найкращий результат ({direction}): {best.score} {sport.unit} (Спортсмен ID {best.athlete_id})")
        print(f"Середній результат по дисципліні: {avg_score} {sport.unit}")

        print("\nПідсумкова таблиця рейтингу:")
        ranking = service.build_ranking(sport.id)
        print(f"{'Місце':<6} | {'Спортсмен':<22} | {'Країна':<10} | {'Результат':<12} | {'Категорія':<10} | {'Змагання'}")
        print("-" * 85)
        for row in ranking:
            res_str = f"{row['score']} {row['unit']}"
            print(
                f"{row['rank']:<6} | {row['athlete_name']:<22} | {row['country']:<10} | "
                f"{res_str:<12} | {row['category']:<10} | {row['competition']}"
            )


def demonstrate_dbapi_queries() -> None:
    """Демонстрація виконання безпечних параметризованих запитів DB-API та агрегації SQL."""
    print("\n--- Демонстрація прямого Python DB-API (sqlite3) ---")
    sport_name = "Біг на 100м"
    print(f"1. Параметризований запит результатів для виду спорту '{sport_name}':")
    results = find_results_by_sport_dbapi(DB_PATH, sport_name)
    for r in results:
        comp = r['competition_name'] or 'Не вказано'
        print(f" - Спортсмен: {r['athlete_name']}, Результат: {r['score']} {r['unit']}, Змагання: {comp}")

    print(f"\n2. Агрегатна статистика SQL (COUNT, AVG, MIN, MAX) для '{sport_name}':")
    stats = get_sport_statistics_dbapi(DB_PATH, sport_name)
    if stats:
        print(f" - Всього залікових виступів: {stats['total_results']}")
        print(f" - Середній результат (AVG): {stats['avg_score']} {stats['unit']}")
        print(f" - Мінімум (MIN): {stats['min_score']} {stats['unit']}")
        print(f" - Максимум (MAX): {stats['max_score']} {stats['unit']}")


def main() -> None:
    """Головна точка входу."""
    print("=" * 70)
    print(" ЛАБОРАТОРНА РОБОТА №7: РОБОТА З БАЗАМИ ДАНИХ У PYTHON")
    print(" Варіант №9: Облік спортивних результатів")
    print("=" * 70)

    # 1. Створення таблиць
    initialize_database()

    # 2. Сесія та сервісний шар
    engine = get_engine(DB_URL)
    session_factory = get_session_factory(engine)
    session = session_factory()

    try:
        service = SportsService(session)

        # Перевіряємо наявність даних
        existing_sports = service.sports_repo.list_all()
        if not existing_sports:
            seed_sample_data(service)
        else:
            print("\nБаза даних вже містить попередньо завантажені дані.")

        # Демонстрація транзакцій
        demonstrate_acid_transaction(service)

        # Аналітика та рейтинг
        display_analytics_and_ranking(service)

        # DB-API запити
        demonstrate_dbapi_queries()

    finally:
        session.close()

    print("\n" + "=" * 70)
    print(" Виконання лабораторної роботи успішно завершено.")
    print("=" * 70)


if __name__ == "__main__":
    main()
