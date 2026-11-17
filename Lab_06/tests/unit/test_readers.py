"""Тестування потокового читання CSV (CsvResultsReader)."""

from pathlib import Path
import pytest

from sports_accounting.exceptions import DataImportError
from sports_accounting.readers import CsvResultsReader


def test_csv_reader_missing_file_raises(tmp_path: Path) -> None:
    reader = CsvResultsReader()
    missing = tmp_path / "missing.csv"
    with pytest.raises(DataImportError, match="Файл не знайдено"):
        list(reader.read(missing))


def test_csv_reader_empty_file_raises(tmp_path: Path) -> None:
    reader = CsvResultsReader()
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(DataImportError, match="Файл порожній або не містить заголовків"):
        list(reader.read(empty))


def test_csv_reader_valid_streaming(tmp_path: Path) -> None:
    reader = CsvResultsReader()
    valid_csv = tmp_path / "data.csv"
    valid_csv.write_text("id,val\n1,A\n2,B\n", encoding="utf-8")
    rows = list(reader.read(valid_csv))
    assert len(rows) == 2
    assert rows[0] == (2, {"id": "1", "val": "A"})
    assert rows[1] == (3, {"id": "2", "val": "B"})
