"""Streaming analytics and aggregations: average, min/max, pairwise analysis."""

from collections import Counter
from collections.abc import Iterable
from itertools import pairwise
from typing import Any

from stream_processor.models import SportsRecord


def streaming_average(records: Iterable[SportsRecord]) -> float:
    """Compute arithmetic average in a single streaming pass with O(1) memory."""
    total = 0.0
    count = 0
    for r in records:
        total += r.result
        count += 1
    return round(total / count, 2) if count else 0.0


def calculate_stream_statistics(records: Iterable[SportsRecord]) -> dict[str, Any]:
    """Calculate count, total, average, min, max, and category frequencies in one pass."""
    count = 0
    total = 0.0
    min_res: float | None = None
    max_res: float | None = None
    best_athlete: str | None = None
    categories = Counter()
    sports = Counter()

    for r in records:
        count += 1
        total += r.result
        categories[r.category] += 1
        sports[r.sport] += 1

        if min_res is None or r.result < min_res:
            min_res = r.result
        if max_res is None or r.result > max_res:
            max_res = r.result
            best_athlete = r.athlete

    avg = round(total / count, 2) if count else 0.0
    return {
        "count": count,
        "total": round(total, 2),
        "average": avg,
        "minimum": min_res,
        "maximum": max_res,
        "best_athlete": best_athlete,
        "categories": dict(categories),
        "sports": dict(sports),
    }


def analyze_consecutive_differences(records: Iterable[SportsRecord]) -> list[tuple[str, str, float]]:
    """Pairwise analysis of sequential score changes using itertools.pairwise."""
    diffs = []
    for prev, curr in pairwise(records):
        diff = round(curr.result - prev.result, 2)
        diffs.append((prev.athlete, curr.athlete, diff))
    return diffs
