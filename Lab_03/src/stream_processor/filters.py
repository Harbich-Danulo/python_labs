"""Streaming validation and filtering stages for sports records."""

from collections.abc import Iterable, Iterator
from typing import Callable

from stream_processor.models import SportsRecord


def validate_records(
    rows: Iterable[dict[str, str]],
    invalid_counter: list[int] | None = None,
) -> Iterator[SportsRecord]:
    """Validate streaming raw records into SportsRecord instances, skipping invalid rows."""
    for row in rows:
        try:
            athlete = row.get("athlete", "").strip()
            sport = row.get("sport", "").strip()
            category = row.get("category", "").strip()
            timestamp = row.get("timestamp", "").strip()
            result_val = float(row.get("result", ""))

            # Validation criteria
            if not athlete or not sport or not category:
                if invalid_counter is not None:
                    invalid_counter[0] += 1
                continue
            if result_val < 0:
                if invalid_counter is not None:
                    invalid_counter[0] += 1
                continue

            yield SportsRecord(
                athlete=athlete,
                sport=sport,
                result=result_val,
                category=category,
                timestamp=timestamp,
            )
        except (ValueError, TypeError, KeyError):
            if invalid_counter is not None:
                invalid_counter[0] += 1
            continue


def filter_by_sport(
    records: Iterable[SportsRecord],
    sport: str,
) -> Iterator[SportsRecord]:
    """Filter records by sport discipline lazily."""
    target = sport.strip().lower()
    for record in records:
        if record.sport.strip().lower() == target:
            yield record


def filter_by_category(
    records: Iterable[SportsRecord],
    category: str,
) -> Iterator[SportsRecord]:
    """Filter records by athlete category lazily."""
    target = category.strip().lower()
    for record in records:
        if record.category.strip().lower() == target:
            yield record


def filter_by_predicate(
    records: Iterable[SportsRecord],
    predicate: Callable[[SportsRecord], bool],
) -> Iterator[SportsRecord]:
    """Universal lazy filter stage."""
    for record in records:
        if predicate(record):
            yield record
