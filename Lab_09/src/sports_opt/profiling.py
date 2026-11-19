"""Модуль профілювання продуктивності: час викликів (cProfile) та використання пам'яті (tracemalloc)."""

from __future__ import annotations
import cProfile
import io
import pstats
import tracemalloc
from typing import Any, Callable, Dict, List, Tuple


def profile_execution_cprofile(
    target_func: Callable[..., Any], *args: Any, sort_by: str = "cumulative", top_n: int = 15
) -> str:
    """Виконує точне профілювання викликів функцій та повертає текстову таблицю pstats."""
    profiler = cProfile.Profile()
    profiler.enable()
    target_func(*args)
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats(sort_by)
    stats.print_stats(top_n)
    return stream.getvalue()


def profile_memory_tracemalloc(
    target_func: Callable[..., Any], *args: Any, top_n: int = 10
) -> Tuple[float, float, List[str]]:
    """Вимірює споживання пам'яті (поточна та пікова у МБ) і джерела виділення (snapshot)."""
    tracemalloc.start()
    tracemalloc.reset_peak()

    target_func(*args)

    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()

    current_mb = current_bytes / (1024 * 1024)
    peak_mb = peak_bytes / (1024 * 1024)

    stat_lines: List[str] = []
    top_stats = snapshot.statistics("lineno")
    for stat in top_stats[:top_n]:
        stat_lines.append(str(stat))

    return (current_mb, peak_mb, stat_lines)
