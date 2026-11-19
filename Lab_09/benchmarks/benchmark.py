"""Скрипт повного бенчмаркінгу, порівняння реалізацій, масштабування workers та експорту в CSV."""

from __future__ import annotations
import csv
import os
import sys
import time
from statistics import mean
from typing import Any, Callable, Dict, List, Tuple

# Додаємо src до sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from sports_opt.analytics import (
    calculate_scores_sequential,
    generate_sports_dataset,
    score_complex_transform,
    statistics_numpy,
    statistics_python,
)
from sports_opt.caching import SportsRatingService
from sports_opt.parallel import (
    calculate_scores_processes,
    calculate_scores_threads,
)
from sports_opt.profiling import profile_memory_tracemalloc


def benchmark_repeated(
    func: Callable[..., Any], *args: Any, repeats: int = 5
) -> Tuple[float, float]:
    """Вимірює середній час виконання за repeats прогонів та пікову пам'ять у МБ."""
    times: List[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        func(*args)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    # Вимірюємо пам'ять окремим прогоном
    _, peak_mb, _ = profile_memory_tracemalloc(func, *args)
    return (mean(times), peak_mb)


def run_comprehensive_benchmark() -> List[Dict[str, Any]]:
    """Проводить серію експериментів для різних розмірів dataset та конфігурацій workers."""
    dataset_sizes = [10_000, 100_000]
    records: List[Dict[str, Any]] = []

    print("=" * 80)
    print(" ЗАПУСК КОМПЛЕКСНОГО БЕНЧМАРКІНГУ (ЛАБОРАТОРНА РОБОТА №9)")
    print("=" * 80)

    for size in dataset_sizes:
        print(f"\n--- Дослідження розміру вибірки: N = {size} записів ---")
        dataset = generate_sports_dataset(size, seed=42)
        scores = [r.score for r in dataset]

        # 1. Baseline: Sequential Python loops
        t_base, mem_base = benchmark_repeated(statistics_python, scores, repeats=5)
        records.append({
            "dataset_size": size,
            "operation": "Statistics (Python)",
            "method": "Sequential",
            "workers": 1,
            "mean_time_s": round(t_base, 6),
            "peak_memory_mb": round(mem_base, 2),
            "speedup": 1.00,
        })
        print(f"[*] Baseline (Python loops):      {t_base:.6f} s, Memory: {mem_base:.2f} MB, Speedup: 1.00x")

        # 2. NumPy Vectorization
        t_np, mem_np = benchmark_repeated(statistics_numpy, scores, repeats=5)
        sp_np = round(t_base / t_np, 2) if t_np > 0 else 0.0
        records.append({
            "dataset_size": size,
            "operation": "Statistics (NumPy)",
            "method": "NumPy",
            "workers": "-",
            "mean_time_s": round(t_np, 6),
            "peak_memory_mb": round(mem_np, 2),
            "speedup": sp_np,
        })
        print(f"[*] NumPy Vectorization:          {t_np:.6f} s, Memory: {mem_np:.2f} MB, Speedup: {sp_np}x")

        # Дослідження важких CPU-bound обчислень (score_complex_transform) на зрізі даних
        calc_slice = scores[: min(size, 20_000)]
        print(f"  [CPU-bound Transform на зрізі {len(calc_slice)} елементів]")

        # Послідовний розрахунок CPU-bound
        t_calc_seq, mem_calc_seq = benchmark_repeated(calculate_scores_sequential, calc_slice, repeats=3)
        records.append({
            "dataset_size": len(calc_slice),
            "operation": "Transform (CPU-bound)",
            "method": "Sequential",
            "workers": 1,
            "mean_time_s": round(t_calc_seq, 6),
            "peak_memory_mb": round(mem_calc_seq, 2),
            "speedup": 1.00,
        })
        print(f"    - Sequential CPU-bound:       {t_calc_seq:.6f} s, Speedup: 1.00x")

        # ThreadPoolExecutor (1, 2, 4, 8 workers)
        for w in [1, 2, 4, 8]:
            t_th, mem_th = benchmark_repeated(calculate_scores_threads, calc_slice, w, repeats=3)
            sp_th = round(t_calc_seq / t_th, 2) if t_th > 0 else 0.0
            records.append({
                "dataset_size": len(calc_slice),
                "operation": "Transform (CPU-bound)",
                "method": f"ThreadPool (w={w})",
                "workers": w,
                "mean_time_s": round(t_th, 6),
                "peak_memory_mb": round(mem_th, 2),
                "speedup": sp_th,
            })
            print(f"    - ThreadPool (workers={w}):     {t_th:.6f} s, Speedup: {sp_th}x")

        # ProcessPoolExecutor (1, 2, 4, 8 workers)
        for w in [1, 2, 4, 8]:
            t_pr, mem_pr = benchmark_repeated(calculate_scores_processes, calc_slice, w, 500, repeats=3)
            sp_pr = round(t_calc_seq / t_pr, 2) if t_pr > 0 else 0.0
            records.append({
                "dataset_size": len(calc_slice),
                "operation": "Transform (CPU-bound)",
                "method": f"ProcessPool (w={w})",
                "workers": w,
                "mean_time_s": round(t_pr, 6),
                "peak_memory_mb": round(mem_pr, 2),
                "speedup": sp_pr,
            })
            print(f"    - ProcessPool (workers={w}):    {t_pr:.6f} s, Speedup: {sp_pr}x")

    # 3. Caching benchmark (Cold vs Warm)
    print("\n--- Дослідження ефективності кешування (Caching) ---")
    service = SportsRatingService(generate_sports_dataset(50_000))
    service.clear_cache()

    # Холодний виклик (розрахунок)
    start_cold = time.perf_counter()
    service.calculate_stats_cached(sport_id=1)
    t_cold = time.perf_counter() - start_cold

    # Гарячий виклик (із кешу)
    start_warm = time.perf_counter()
    for _ in range(1000):
        service.calculate_stats_cached(sport_id=1)
    t_warm = (time.perf_counter() - start_warm) / 1000.0

    sp_cache = round(t_cold / t_warm, 2) if t_warm > 0 else 0.0
    records.append({
        "dataset_size": 50_000,
        "operation": "Sport Stats Cache",
        "method": "Cold Call",
        "workers": "-",
        "mean_time_s": round(t_cold, 6),
        "peak_memory_mb": 0.01,
        "speedup": 1.00,
    })
    records.append({
        "dataset_size": 50_000,
        "operation": "Sport Stats Cache",
        "method": "Warm Call (LRU Cache)",
        "workers": "-",
        "mean_time_s": round(t_warm, 8),
        "peak_memory_mb": 0.01,
        "speedup": sp_cache,
    })
    print(f"[*] Cold call (uncached):        {t_cold:.6f} s")
    print(f"[*] Warm call (lru_cache):       {t_warm:.8f} s, Speedup: {sp_cache}x")

    # Експорт результатів у CSV
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "benchmark_results.csv"))
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    print(f"\n[OK] Результати успішно збережено у файл: {csv_path}")
    return records


if __name__ == "__main__":
    run_comprehensive_benchmark()
