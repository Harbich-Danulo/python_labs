"""Модуль потокового читання файлів CSV."""

from collections.abc import Iterator
import csv
from pathlib import Path

from sports_accounting.exceptions import DataImportError


class CsvResultsReader:
    """Потоковий рідер CSV файлів спортивних результатів."""

    def read(self, path: Path) -> Iterator[tuple[int, dict[str, str]]]:
        if not path.exists():
            raise DataImportError(f"Файл не знайдено: {path}")

        try:
            with path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames is None:
                    raise DataImportError(f"Файл порожній або не містить заголовків: {path}")
                for line_number, row in enumerate(reader, start=2):
                    yield line_number, row
        except OSError as error:
            raise DataImportError(f"Помилка вводу/виводу при читанні '{path}': {error}") from error
