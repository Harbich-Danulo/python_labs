"""Main application entry point demonstrating domain models, SOLID principles, and type safety."""

from sports_app.dto import ResultPayload
from sports_app.models import (
    Athlete,
    AthleteCategory,
    Competition,
    HigherScoreWinsStrategy,
    LowerTimeWinsStrategy,
    RankingTable,
    Result,
    Sport,
)
from sports_app.repositories import InMemoryRepository
from sports_app.services import (
    ConsoleNotifier,
    MarkdownExporter,
    SportsAccountingService,
)
from sports_app.value_objects import Score


def build_sample_service() -> SportsAccountingService:
    """Build and wire application service using manual Dependency Injection container pattern."""
    athlete_repo = InMemoryRepository[Athlete]()
    result_repo = InMemoryRepository[Result]()
    notifier = ConsoleNotifier()
    exporter = MarkdownExporter()

    service = SportsAccountingService(
        athlete_repo=athlete_repo,
        result_repo=result_repo,
        notifier=notifier,
        exporter=exporter,
    )
    return service


def seed_demo_data(service: SportsAccountingService) -> None:
    """Populate service with initial Ukrainian sports achievements using TypedDict payloads."""
    payloads: list[ResultPayload] = [
        {
            "result_id": 101,
            "athlete_id": 1,
            "athlete_name": "Ярослава Магучіх",
            "country": "Україна",
            "age": 22,
            "sport_name": "Стрибки у висоту",
            "competition_name": "Diamond League",
            "location": "Париж",
            "year": 2024,
            "score_value": 2.10,
            "score_unit": "m",
            "category": "Дорослі",
            "notes": "Світовий рекорд",
        },
        {
            "result_id": 102,
            "athlete_id": 2,
            "athlete_name": "Ірина Геращенко",
            "country": "Україна",
            "age": 29,
            "sport_name": "Стрибки у висоту",
            "competition_name": "Олімпійські Ігри",
            "location": "Париж",
            "year": 2024,
            "score_value": 2.00,
            "score_unit": "m",
            "category": "Дорослі",
        },
        {
            "result_id": 103,
            "athlete_id": 3,
            "athlete_name": "Юлія Левченко",
            "country": "Україна",
            "age": 26,
            "sport_name": "Стрибки у висоту",
            "competition_name": "Чемпіонат України",
            "location": "Львів",
            "year": 2024,
            "score_value": 1.95,
            "score_unit": "m",
            "category": "Дорослі",
        },
        {
            "result_id": 104,
            "athlete_id": 4,
            "athlete_name": "Ілля Ковтун",
            "country": "Україна",
            "age": 21,
            "sport_name": "Спортивна гімнастика",
            "competition_name": "Олімпійські Ігри",
            "location": "Париж",
            "year": 2024,
            "score_value": 15.65,
            "score_unit": "pts",
            "category": "Юніори",
        },
        {
            "result_id": 105,
            "athlete_id": 5,
            "athlete_name": "Олег Верняєв",
            "country": "Україна",
            "age": 30,
            "sport_name": "Спортивна гімнастика",
            "competition_name": "Олімпійські Ігри",
            "location": "Париж",
            "year": 2024,
            "score_value": 15.30,
            "score_unit": "pts",
            "category": "Майстри",
        },
        {
            "result_id": 106,
            "athlete_id": 6,
            "athlete_name": "Михайло Романчук",
            "country": "Україна",
            "age": 28,
            "sport_name": "Плавання 800м",
            "competition_name": "Олімпійські Ігри",
            "location": "Токіо",
            "year": 2021,
            "score_value": 461.50,
            "score_unit": "s",
            "category": "Дорослі",
        },
        {
            "result_id": 107,
            "athlete_id": 7,
            "athlete_name": "Олександр Желтяков",
            "country": "Україна",
            "age": 18,
            "sport_name": "Плавання 800м",
            "competition_name": "Чемпіонат Європи",
            "location": "Белград",
            "year": 2024,
            "score_value": 472.10,
            "score_unit": "s",
            "category": "Юніори",
        },
    ]

    for p in payloads:
        service.register_result_from_payload(p)


def main() -> None:
    """Demonstration scenario for Laboratory Work 4."""
    print("=" * 75)
    print("  ЛАБОРАТОРНА РОБОТА №4: ПРОФЕСІЙНЕ ООП ТА СИСТЕМА ТИПІВ PYTHON")
    print("  Варіант 9: Система обліку спортивних результатів")
    print("=" * 75)

    # 1. Dependency Injection setup
    print("\n[1] Ініціалізація сервісу через Dependency Injection:")
    service = build_sample_service()

    # 2. Registration via DTO TypedDict
    print("\n[2] Реєстрація спортивних результатів (DTO Payload -> Domain Entity):")
    seed_demo_data(service)

    # 3. Value Object immutability & arithmetic
    print("\n[3] Демонстрація Value Object Score (frozen=True, slots=True, __add__):")
    s1 = Score(2.10, "m")
    s2 = Score(0.05, "m")
    s_sum = s1 + s2
    print(f"  {s1} + {s2} = {s_sum} (Тип: {type(s_sum).__name__})")

    # 4. Пошук за видом спорту
    sport_name = "Стрибки у висоту"
    print(f"\n[4] Пошук за видом спорту '{sport_name}':")
    jump_results = service.find_by_sport(sport_name)
    for res in jump_results:
        print(f"  * {res.athlete.name:<22} | {res.score} | {res.competition.name}")

    # 5. Визначення найкращого результату
    best = service.find_best_result(sport_name)
    if best:
        print(f"\n[5] Найкращий результат у дисципліні '{sport_name}':")
        print(f"  Рекордсмен: {best.athlete.name} — {best.score} ({best.category.value})")

    # 6. Статистичний аналіз
    stats = service.calculate_statistics(sport_name)
    if stats:
        print(f"\n[6] Розрахунок статистики для '{sport_name}':")
        print(f"  Кількість спроб:     {stats.sample_size}")
        print(f"  Сумарна висота:      {stats.total_score}")
        print(f"  Середня висота:      {stats.average_score}")
        print(f"  Максимальна висота:  {stats.highest_score}")
        print(f"  Мінімальна висота:   {stats.lowest_score}")

    # 7. Контейнер RankingTable та Dunder методи (__len__, __iter__, __contains__, __getitem__)
    table = service.build_ranking_table(sport_name)
    print(f"\n[7] Контейнер RankingTable (Dunder методи: len={len(table)}, '101 in table'={101 in table}):")
    print(f"  Лідер таблиці (table[0]): {table[0].athlete.name} з результатом {table[0].score}")
    print("\n  Повна рейтингова таблиця (ітерація __iter__):")
    for pos, item in enumerate(table, start=1):
        print(f"    {pos}. {item.athlete.name:<22} : {item.score} ({item.category.value})")

    # 8. Стратегія сортування часу (LowerTimeWinsStrategy)
    swim_sport = "Плавання 800м"
    swim_table = service.build_ranking_table(swim_sport)
    print(f"\n[8] Рейтинг для часової дисципліни '{swim_sport}' (Стратегія: менший час кращий):")
    for pos, item in enumerate(swim_table, start=1):
        print(f"    {pos}. {item.athlete.name:<22} : {item.score} ({item.category.value})")

    # 9. Експорт звіту через Protocol
    print("\n[9] Генерація та експорт звіту (ResultExporter Protocol):")
    report_text = service.export_report(sport_name)
    print(report_text)


if __name__ == "__main__":
    main()
