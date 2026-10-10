"""Unit tests for Laboratory Work 3 stream processor."""

from pathlib import Path
from itertools import islice

from stream_processor.analytics import (
    analyze_consecutive_differences,
    calculate_stream_statistics,
    streaming_average,
)
from stream_processor.filters import filter_by_sport, validate_records
from stream_processor.models import SportsRange, SportsRangeIterator, SportsRecord
from stream_processor.parsers import parse_csv_rows
from stream_processor.pipeline import build_pipeline
from stream_processor.transformations import batched_records, normalize_athlete_names


def test_custom_iterator():
    r = SportsRange(1, 4)
    it = iter(r)
    assert isinstance(it, SportsRangeIterator)
    assert list(it) == [1, 2, 3]


def test_pipeline_on_sample_data():
    sample_path = Path("c:/labs/lab3/data/input.csv")
    assert sample_path.exists()

    invalids = [0]
    stream = build_pipeline(sample_path, invalid_counter=invalids)
    records = list(stream)

    assert len(records) == 9  # 12 rows minus 3 invalid rows
    assert invalids[0] == 3
    assert records[0].athlete == "Ярослава Магучіх"


def test_streaming_average():
    sample_path = Path("c:/labs/lab3/data/input.csv")
    stream = build_pipeline(sample_path, sport_filter="Стрибки у висоту")
    avg = streaming_average(stream)
    # Jumpers valid: Магучіх (2.10), Геращенко (2.00), Левченко (1.95), Лавський (2.25)
    # Sum: 8.30 / 4 = 2.075 -> 2.08
    assert avg == 2.08


def test_batching():
    sample_path = Path("c:/labs/lab3/data/input.csv")
    stream = build_pipeline(sample_path)
    batches = list(batched_records(stream, batch_size=4))
    assert len(batches) == 3  # 4 + 4 + 1 = 9 records
    assert len(batches[0]) == 4
    assert len(batches[2]) == 1


def test_pairwise():
    sample_path = Path("c:/labs/lab3/data/input.csv")
    stream = build_pipeline(sample_path, sport_filter="Стрибки у висоту")
    diffs = analyze_consecutive_differences(stream)
    assert len(diffs) == 3


if __name__ == "__main__":
    test_custom_iterator()
    test_pipeline_on_sample_data()
    test_streaming_average()
    test_batching()
    test_pairwise()
    print("All tests passed successfully!")
