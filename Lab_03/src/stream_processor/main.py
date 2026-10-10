"""Main application module for Laboratory Work 3: Streaming sports results processing and benchmarks."""

import csv
from itertools import chain, islice, pairwise
from pathlib import Path
import random
from time import perf_counter
from typing import Any
import tracemalloc

from stream_processor.analytics import (
    analyze_consecutive_differences,
    calculate_stream_statistics,
    streaming_average,
)
from stream_processor.filters import filter_by_sport
from stream_processor.models import SportsRange, SportsRecord
from stream_processor.pipeline import build_pipeline
from stream_processor.transformations import batched_records


def generate_large_dataset(path: Path, count: int) -> None:
    """Generate large CSV dataset for streaming experiments without loading it into memory."""
    sports_pool = [
        ("Стрибки у висоту", 1.80, 2.15),
        ("Спортивна гімнастика", 13.0, 16.0),
        ("Плавання", 800.0, 950.0),
        ("Стрибки у довжину", 6.0, 7.2),
        ("Біг 100м", 9.8, 12.0),
    ]
    categories = ["Дорослі", "Юніори", "Майстри"]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["athlete", "sport", "result", "category", "timestamp"])

        for i in range(1, count + 1):
            sport, min_r, max_r = random.choice(sports_pool)
            res = round(random.uniform(min_r, max_r), 2)
            cat = random.choice(categories)
            writer.writerow([f"Athlete_{i}", sport, res, cat, f"2024-08-01T{i%24:02d}:00:00"])


def eager_read_all(path: Path) -> list[dict[str, str]]:
    """Eager reader: materializes the entire file in RAM as a list of dicts."""
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def run_benchmarks(data_dir: Path) -> list[dict[str, Any]]:
    """Compare eager vs lazy processing across 10k, 100k, 500k records for time, memory and time-to-first-result."""
    counts = [10_000, 100_000, 500_000]
    bench_results = []

    print("\n" + "=" * 75)
    print("  ЕКСПЕРИМЕНТАЛЬНА ЧАСТИНА: ПОРІВНЯННЯ EAGER ТА LAZY PROCESSING")
    print("=" * 75)

    for count in counts:
        file_path = data_dir / f"test_{count}.csv"
        if not file_path.exists():
            print(f"Генерація вибірки {count:,} записів -> {file_path.name}...")
            generate_large_dataset(file_path, count)

        # 1. Eager measurement
        tracemalloc.start()
        t0 = perf_counter()
        eager_data = eager_read_all(file_path)
        # Process in memory
        eager_filtered = [r for r in eager_data if r.get("sport") == "Плавання"]
        eager_total = sum(float(r["result"]) for r in eager_filtered)
        eager_count = len(eager_filtered)
        _ = eager_total / eager_count if eager_count else 0
        t_eager = perf_counter() - t0
        _, eager_peak_b = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        eager_peak_mb = round(eager_peak_b / (1024 * 1024), 2)
        del eager_data, eager_filtered

        # 2. Lazy measurement (total stream consumption)
        tracemalloc.start()
        t0 = perf_counter()
        stream = build_pipeline(file_path, sport_filter="Плавання")
        _ = streaming_average(stream)
        t_lazy = perf_counter() - t0
        _, lazy_peak_b = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        lazy_peak_mb = round(lazy_peak_b / (1024 * 1024), 2)

        # 3. Time to first result (Early termination)
        t0 = perf_counter()
        first_stream = build_pipeline(file_path, sport_filter="Плавання")
        _ = next(first_stream, None)
        t_first = perf_counter() - t0

        res_entry = {
            "records": count,
            "eager_time": round(t_eager, 4),
            "lazy_time": round(t_lazy, 4),
            "eager_mem": eager_peak_mb,
            "lazy_mem": lazy_peak_mb,
            "time_to_first": round(t_first, 6),
            "mem_ratio": round(eager_peak_mb / max(lazy_peak_mb, 0.01), 1),
        }
        bench_results.append(res_entry)

        print(
            f"Records: {count:>7} | Eager: {t_eager:.4f}s ({eager_peak_mb:>6.2f} MB) | "
            f"Lazy: {t_lazy:.4f}s ({lazy_peak_mb:>5.2f} MB) | First record: {t_first:.6f}s | "
            f"Економія RAM: {res_entry['mem_ratio']}x"
        )

        # Cleanup test file after run to save disk space
        try:
            file_path.unlink()
        except OSError:
            pass

    return bench_results


def main() -> None:
    """Execute main pipeline workflow for Laboratory Work 3."""
    print("=" * 75)
    print("  ЛАБОРАТОРНА РОБОТА №3: ІТЕРАТОРИ, ГЕНЕРАТОРИ ТА ПОТОКОВА ОБРОБКА ДАНИХ")
    print("  Варіант 9: Потокова обробка спортивних результатів")
    print("=" * 75)

    base_dir = Path("c:/labs/lab3")
    sample_csv = base_dir / "data" / "input.csv"

    # 1. Custom Iterable & Iterator demonstration
    print("\n[1] Власний клас ітератора SportsRange(1, 4):")
    custom_range = SportsRange(1, 4)
    print(f"  Елементи ітератора: {list(custom_range)}")

    # 2. Streaming pipeline demonstration on sample data
    print(f"\n[2] Запуск потокового конвеєра для файлу: {sample_csv.name}")
    invalid_rows = [0]
    stream = build_pipeline(sample_csv, invalid_counter=invalid_rows)

    # 3. islice: отримання перших N записів без читання всього файлу
    print("\n[3] Перші 3 валідні записи через itertools.islice:")
    first_three = list(islice(stream, 3))
    for r in first_three:
        print(f"  * {r.athlete:<22} | {r.sport:<20} | {r.result:<6.2f} | {r.category}")

    # 4. Повна статистика без матеріалізації колекції (перезапуск генератора)
    stream_for_stats = build_pipeline(sample_csv)
    stats = calculate_stream_statistics(stream_for_stats)
    print("\n[4] Потокова статистика (calculate_stream_statistics):")
    print(f"  Кількість валідних записів: {stats['count']}")
    print(f"  Відкинуто некоректних рядків: {invalid_rows[0]}")
    print(f"  Середній результат:          {stats['average']:.2f}")
    print(f"  Найкращий результат:         {stats['maximum']} ({stats['best_athlete']})")
    print(f"  Розподіл за категоріями:     {stats['categories']}")
    print(f"  Розподіл за дисциплінами:    {stats['sports']}")

    # 5. Generator expression
    stream_for_gen = build_pipeline(sample_csv, sport_filter="Стрибки у висоту")
    high_jump_scores = (r.result for r in stream_for_gen)  # Generator expression
    print(f"\n[5] Generator expression: сума балів стрибунів у висоту = {sum(high_jump_scores):.2f}")

    # 6. Batch processing
    stream_for_batch = build_pipeline(sample_csv)
    print("\n[6] Пакетна обробка (Batching) по 4 записи:")
    for b_idx, batch in enumerate(batched_records(stream_for_batch, batch_size=4), start=1):
        names = ", ".join(r.athlete for r in batch)
        print(f"  Пакет #{b_idx} ({len(batch)} записів): {names}")

    # 7. itertools.pairwise аналіз
    stream_for_pairwise = build_pipeline(sample_csv, sport_filter="Стрибки у висоту")
    diffs = analyze_consecutive_differences(stream_for_pairwise)
    print("\n[7] Аналіз динаміки результатів через itertools.pairwise (Стрибки у висоту):")
    for prev_ath, curr_ath, diff in diffs:
        sign = "+" if diff > 0 else ""
        print(f"  {prev_ath} -> {curr_ath}: {sign}{diff:.2f} м")

    # 8. itertools.chain (об'єднання потоків)
    stream_a = build_pipeline(sample_csv, sport_filter="Плавання")
    stream_b = build_pipeline(sample_csv, sport_filter="Спортивна гімнастика")
    chained = chain(stream_a, stream_b)
    print("\n[8] Об'єднання потоків через itertools.chain (Плавання + Гімнастика):")
    for r in chained:
        print(f"  - {r.athlete:<20} ({r.sport}) : {r.result:.2f}")

    # 9. Експериментальна частина (Eager vs Lazy, Memory & Time)
    run_benchmarks(base_dir / "data")


if __name__ == "__main__":
    main()
