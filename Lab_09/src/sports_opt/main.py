"""Головна точка входу: демонстрація профілювання, виявлення bottleneck, паралельності та кешування."""

from __future__ import annotations
import threading
import time
from sports_opt.analytics import (
    calculate_scores_sequential,
    generate_sports_dataset,
    score_complex_transform,
    statistics_numpy,
    statistics_python,
)
from sports_opt.caching import SportsRatingService, get_cache_metrics
from sports_opt.models import SportResult
from sports_opt.parallel import (
    ThreadSafeResultTracker,
    calculate_scores_processes,
    calculate_scores_threads,
)
from sports_opt.profiling import profile_execution_cprofile, profile_memory_tracemalloc


def demonstrate_profiling_and_bottleneck() -> None:
    """1. Демонстрація cProfile та знаходження вузького місця (bottleneck)."""
    print("\n" + "=" * 70)
    print(" 1. ПРОФІЛЮВАННЯ ПРОДУКТИВНОСТІ (cProfile) ТА ПОШУК BOTTLENECK")
    print("=" * 70)

    dataset = generate_sports_dataset(15_000, seed=42)
    scores = [r.score for r in dataset]

    print(f"Згенеровано набір даних: {len(scores)} спортивних результатів.")
    print("Виконання профілювання cProfile для функції calculate_scores_sequential...")

    profile_text = profile_execution_cprofile(calculate_scores_sequential, scores, top_n=8)
    print("\nРезультати профілювання (сортування за cumulative time):")
    print(profile_text)


def demonstrate_memory_profiling() -> None:
    """2. Демонстрація вимірювання пам'яті через tracemalloc."""
    print("\n" + "=" * 70)
    print(" 2. АНАЛІЗ ВИКОРИСТАННЯ ПАМ'ЯТІ (tracemalloc)")
    print("=" * 70)

    def memory_workload() -> list[SportResult]:
        return generate_sports_dataset(100_000, seed=42)

    current_mb, peak_mb, top_stats = profile_memory_tracemalloc(memory_workload, top_n=4)
    print(f"Поточна задіяна пам'ять: {current_mb:.2f} МБ")
    print(f"Пікове використання пам'яті: {peak_mb:.2f} МБ")
    print("\nТоп джерел виділення пам'яті за рядками коду:")
    for stat in top_stats:
        print(f" - {stat}")


def demonstrate_synchronization_and_race_condition() -> None:
    """3. Демонстрація Race Condition та коректної синхронізації через Lock."""
    print("\n" + "=" * 70)
    print(" 3. СИНХРОНІЗАЦІЯ ПОТОКІВ (Lock) ТА ЗАПОБІГАННЯ RACE CONDITION")
    print("=" * 70)

    tracker = ThreadSafeResultTracker()
    iterations_per_thread = 5_000
    num_threads = 4
    expected_total = iterations_per_thread * num_threads

    # Небезпечне оновлення без блокування
    def run_unsafe() -> None:
        for _ in range(iterations_per_thread):
            tracker.increment_unsafe()

    threads: list[threading.Thread] = []
    for _ in range(num_threads):
        t = threading.Thread(target=run_unsafe)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    print(f"Очікуване значення лічильника: {expected_total}")
    print(f"Фактичне значення БЕЗ Lock (Race Condition): {tracker.counter}")

    # Безпечне оновлення з використанням Lock
    tracker.reset()
    def run_safe() -> None:
        for _ in range(iterations_per_thread):
            tracker.increment_safe()

    threads_safe: list[threading.Thread] = []
    for _ in range(num_threads):
        t = threading.Thread(target=run_safe)
        threads_safe.append(t)
        t.start()
    for t in threads_safe:
        t.join()

    print(f"Фактичне значення З ВИКОРИСТАННЯМ Lock: {tracker.counter} (коректно синхронізовано)")


def demonstrate_caching_and_invalidation() -> None:
    """4. Демонстрація LRU-кешу та інвалідації при оновленні результатів."""
    print("\n" + "=" * 70)
    print(" 4. КЕШУВАННЯ (lru_cache) ТА ІНВАЛІДАЦІЯ КЕШУ (Cache Invalidation)")
    print("=" * 70)

    dataset = generate_sports_dataset(20_000, seed=42)
    service = SportsRatingService(dataset)
    service.clear_cache()

    # 1-й виклик (Cold Call)
    t0 = time.perf_counter()
    res1 = service.calculate_stats_cached(sport_id=1)
    dur1 = time.perf_counter() - t0
    print(f"1-й холодний виклик (розрахунок): час = {dur1:.6f} с, результат = {res1[:2]}")

    # 2-й виклик (Warm Call - з кешу)
    t1 = time.perf_counter()
    res2 = service.calculate_stats_cached(sport_id=1)
    dur2 = time.perf_counter() - t1
    print(f"2-й теплий виклик (з кешу):       час = {dur2:.8f} с, результат = {res2[:2]}")
    print(f"Прискорення від кешування:        {dur1 / dur2 if dur2 > 0 else 0.0:.1f}x")

    metrics = get_cache_metrics()
    print(f"Метрики кешу: hits={metrics['hits']}, misses={metrics['misses']}")

    # Додавання нового результату -> інвалідація кешу (зміна версії)
    print("\nДодавання нового екстремального результату (score=25.0 сек) для виду спорту 1...")
    new_result = SportResult(
        id=999999,
        athlete_id=1,
        athlete_name="Данило Гарбіч",
        sport_id=1,
        sport_name="Біг на 100м",
        score=25.0,
        category="Дорослі",
    )
    service.add_result(new_result)

    # 3-й виклик після інвалідації (повинен перерахуватися)
    t2 = time.perf_counter()
    res3 = service.calculate_stats_cached(sport_id=1)
    dur3 = time.perf_counter() - t2
    print(f"3-й виклик після інвалідації:     час = {dur3:.6f} с, оновлений результат = {res3[:2]}")
    assert res3 != res1, "Кеш повинен був оновитися та відобразити нові дані!"
    print("Успіх: кеш автоматично інвалідовано, дані оновлено!")


def main() -> None:
    print("*" * 75)
    print(" ЛАБОРАТОРНА РОБОТА №9")
    print(" ПАРАЛЕЛЬНІСТЬ, БАГАТОПРОЦЕСНІСТЬ ТА ОПТИМІЗАЦІЯ")
    print(" Варіант №9: Облік спортивних результатів")
    print("*" * 75)

    demonstrate_profiling_and_bottleneck()
    demonstrate_memory_profiling()
    demonstrate_synchronization_and_race_condition()
    demonstrate_caching_and_invalidation()

    print("\n" + "*" * 75)
    print(" Демонстраційний сценарій успішно виконано.")
    print(" Для запуску повного бенчмарку виконайте: python benchmarks/benchmark.py")
    print("*" * 75)


if __name__ == "__main__":
    main()
