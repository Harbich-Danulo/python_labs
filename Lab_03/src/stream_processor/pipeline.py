"""Pipeline builder for assembling streaming processing stages."""

from collections.abc import Iterator
from pathlib import Path

from stream_processor.filters import filter_by_category, filter_by_sport, validate_records
from stream_processor.models import SportsRecord
from stream_processor.parsers import parse_csv_rows
from stream_processor.readers import clean_lines, read_lines
from stream_processor.transformations import normalize_athlete_names


def build_pipeline(
    path: Path,
    sport_filter: str | None = None,
    category_filter: str | None = None,
    invalid_counter: list[int] | None = None,
) -> Iterator[SportsRecord]:
    """Assemble a lazy streaming pipeline from file reader to transformed SportsRecords."""
    raw_lines = read_lines(path)
    cleaned = clean_lines(raw_lines)
    parsed = parse_csv_rows(cleaned)
    valid = validate_records(parsed, invalid_counter=invalid_counter)
    normalized = normalize_athlete_names(valid)

    if sport_filter:
        normalized = filter_by_sport(normalized, sport_filter)
    if category_filter:
        normalized = filter_by_category(normalized, category_filter)

    return normalized
