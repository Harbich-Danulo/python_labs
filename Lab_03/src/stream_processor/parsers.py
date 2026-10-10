"""CSV row parser using streaming yield from generator."""

import csv
from collections.abc import Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    """Parse streaming lines into dictionaries without loading entire dataset."""
    reader = csv.DictReader(lines)
    yield from reader
