"""Main application entry point for Laboratory Work 2."""

import random
from time import perf_counter
from typing import Any

from data_processor.analytics import (
    calculate_average,
    calculate_average_values,
    create_category_filter,
    create_record,
    create_result_filter,
    find_best_athlete,
    pipeline_processing,
    sort_by_result,
    universal_sort,
)
from data_processor.data import all_categories, athletes
from data_processor.decorators import operation_history, repeat
from data_processor.processors import (
    count_by_category,
    count_by_sport,
    create_id_index,
    filter_by_sport,
    get_unique_categories,
    get_unique_sports,
    group_by_category,
    group_by_sport,
    nested_grouping,
    universal_filter,
)


def print_athletes(title: str, items: list[dict[str, Any]]) -> None:
    """Print formatted table of athlete records."""
    print(f"\n=== {title} ===")
    header = f"{'ID':<4} | {'Ім\'я':<22} | {'Вид спорту':<22} | {'Результат':<10} | {'Категорія':<12} | {'Мета':<16}"
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)
    for a in items:
        meta_str = str(a.get("meta", "-"))
        print(
            f"{a['id']:<4} | {a['name']:<22} | {a['sport']:<22} | "
            f"{a['result']:<10.2f} | {a['category']:<12} | {meta_str:<16}"
        )
    print(sep)


def run_benchmarks() -> dict[int, tuple[float, float]]:
    """Compare search in list O(n) vs search in dict O(1) across 1_000, 10_000, 100_000 records."""
    sizes = [1_000, 10_000, 100_000]
    results: dict[int, tuple[float, float]] = {}

    print("\n--- ЕКСПЕРИМЕНТАЛЬНА ЧАСТИНА: БЕНЧМАРК (List Search vs Dict Search) ---")
    for size in sizes:
        # Generate dummy dataset
        dataset = [
            {"id": i, "name": f"Athlete_{i}", "result": round(random.uniform(1.0, 100.0), 2)}
            for i in range(1, size + 1)
        ]
        dict_index = {item["id"]: item for item in dataset}
        target_id = size - 1  # near the end for worst-case linear search

        # 1. Linear search in list
        t0 = perf_counter()
        _ = next((item for item in dataset if item["id"] == target_id), None)
        t_list = perf_counter() - t0

        # 2. Hash-table lookup in dict
        t0 = perf_counter()
        _ = dict_index.get(target_id)
        t_dict = perf_counter() - t0

        results[size] = (t_list, t_dict)
        print(f"Кількість записів: {size:>7} | List: {t_list:.8f} s | Dict: {t_dict:.8f} s | Прискорення: {t_list / max(t_dict, 1e-12):.1f}x")

    return results


@repeat(count=2)
def demo_repeat_action() -> None:
    """Demonstrates parameterized decorator."""
    print("  -> Виконання повторюваної дії через @repeat(2)")


def main() -> None:
    """Execute all demonstration scenarios for Laboratory Work 2."""
    print("=" * 70)
    print("  ЛАБОРАТОРНА РОБОТА №2: СТРУКТУРИ ДАНИХ ТА ФУНКЦІОНАЛЬНА ДЕКОМПОЗИЦІЯ")
    print("  Варіант 9: Облік спортивних результатів")
    print("=" * 70)

    # 1. Початкові структури даних
    print_athletes("Початковий список спортсменів (list of dicts з tuple та set)", athletes)

    # 2. Множини (set comprehension)
    sports_set = get_unique_sports(athletes)
    cat_set = get_unique_categories(athletes)
    print(f"\n[SET] Унікальні види спорту ({len(sports_set)}): {sports_set}")
    print(f"[SET] Унікальні категорії ({len(cat_set)}): {cat_set}")
    print(f"[SET] Операція перетину з еталонними категоріями: {cat_set & all_categories}")

    # 3. Швидке індексування (dict comprehension)
    id_index = create_id_index(athletes)
    search_id = 5
    print(f"\n[DICT INDEX] Швидкий пошук за ID={search_id} (O(1)): {id_index.get(search_id)}")

    # 4. Фільтрація (list comprehension)
    jumpers = filter_by_sport(athletes, "Стрибки у висоту")
    print_athletes("Спортсмени дисципліни 'Стрибки у висоту'", jumpers)

    # 5. Групування через defaultdict
    grouped = group_by_sport(athletes)
    print("\n[GROUPING (defaultdict)] Групування спортсменів за видами спорту:")
    for sport_name, members in grouped.items():
        names = ", ".join(m["name"] for m in members)
        print(f"  * {sport_name} ({len(members)}): {names}")

    # 6. Підрахунок через Counter
    sport_counts = count_by_sport(athletes)
    print("\n[COLLECTIONS.COUNTER] Кількість спортсменів за видами спорту:")
    for sport_name, count in sport_counts.items():
        print(f"  * {sport_name}: {count}")

    # 7. Агрегація з декоратором часу (@measure_time)
    avg_score = calculate_average(athletes)
    print(f"[AGGREGATION] Середній результат усіх учасників: {avg_score:.2f}")

    # 8. Сортування та екстремуми (lambda)
    best = find_best_athlete(athletes)
    print(f"\n[LAMBDA MAX] Спортсмен з абсолютним максимумом: {best['name']} ({best['result']:.2f})")
    ranking = sort_by_result(athletes, reverse=True)
    print_athletes("Рейтинг спортсменів за результатом (sorted + lambda)", ranking)

    # 9. Closure (замикання)
    filter_senior = create_category_filter("Дорослі")
    seniors = [a for a in athletes if filter_senior(a)]
    print_athletes("Фільтрація через closure (Категорія: 'Дорослі')", seniors)

    # 10. *args та **kwargs
    sample_avg = calculate_average_values(12.5, 14.0, 18.2, 20.1)
    print(f"\n[*ARGS] Розрахунок середнього з довільної кількості аргументів: {sample_avg:.2f}")

    new_record = create_record(
        id=9,
        name="Жан Беленюк",
        sport="Греко-римська боротьба",
        result=1.0,
        category="Майстри",
        meta=("OG-Gold", "Україна", 2021),
    )
    print(f"[**KWARGS] Створення нового запису спортсмена: {new_record}")

    # 11. Параметризований декоратор
    print("\n[PARAMETERIZED DECORATOR] Демонстрація @repeat(count=2):")
    demo_repeat_action()

    # 12. Вкладене групування (Advanced Task)
    print("\n[ADVANCED] Вкладене групування (Спорт -> Категорія -> Кількість):")
    nested = nested_grouping(athletes)
    for sp, cat_dict in nested.items():
        for cat, aths in cat_dict.items():
            print(f"  * {sp} -> {cat}: {len(aths)} чол.")

    # 13. Pipeline processing (Advanced Task)
    print("\n[ADVANCED] Конвеєрна обробка (Pipeline): Фільтр юніорів -> Сортування за результатом")
    pipe_res = pipeline_processing(
        athletes,
        lambda data: [a for a in data if a["category"] == "Юніори"],
        lambda data: sorted(data, key=lambda a: a["result"], reverse=True),
    )
    print_athletes("Результат конвеєра (Pipeline)", pipe_res)

    # 14. Історія операцій (deque)
    print("\n[COLLECTIONS.DEQUE] Останні операції у системі:")
    for op in operation_history:
        print(f"  - {op}")

    # 15. Експериментальна частина (Бенчмарк)
    run_benchmarks()


if __name__ == "__main__":
    main()
