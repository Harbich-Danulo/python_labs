"""Streaming transformations: title formatting, score adjustments, batching."""

from collections.abc import Iterable, Iterator
from itertools import islice

from stream_processor.models import SportsRecord


def normalize_athlete_names(records: Iterable[SportsRecord]) -> Iterator[SportsRecord]:
    """Lazy transformation stage: title-case athlete names."""
    for record in records:
        yield record._replace(athlete=record.athlete.title())


def batched_records(
    records: Iterable[SportsRecord],
    batch_size: int,
) -> Iterator[list[SportsRecord]]:
    """Yield batches of records using itertools.islice."""
    iterator = iter(records)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            return
        yield batch
