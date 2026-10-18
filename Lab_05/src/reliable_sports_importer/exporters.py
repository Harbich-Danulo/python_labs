"""Атомарний експорт валідних записів у JSON та звітів про помилки."""

from collections.abc import Iterable
import csv
import json
from pathlib import Path
from typing import Any, Protocol

from reliable_sports_importer.exceptions import DataExportError
from reliable_sports_importer.models import InvalidRecordDetail, SportsResult
from reliable_sports_importer.utils import atomic_file_writer


class Exporter(Protocol):
    """Структурний протокол (Task 84.2) для експортерів."""

    def export(self, items: Iterable[SportsResult], target_path: Path) -> int:
        ...


class JsonStreamExporter:
    """Атомарний потоковий експортер результатів у валідний JSON-масив."""

    def export(self, items: Iterable[SportsResult], target_path: Path) -> int:
        count = 0
        try:
            with atomic_file_writer(target_path) as file:
                file.write("[\n")
                first = True
                for item in items:
                    if not first:
                        file.write(",\n")
                    json.dump(item.to_dict(), file, ensure_ascii=False, indent=2)
                    first = False
                    count += 1
                file.write("\n]\n")
        except DataExportError:
            raise
        except Exception as error:
            raise DataExportError(f"Помилка серіалізації в JSON: {error}") from error

        return count


class CsvErrorExporter:
    """Атомарний експорт виявлених помилок у CSV формат (Task 84.5)."""

    def export_errors(self, errors: Iterable[InvalidRecordDetail], target_path: Path) -> int:
        count = 0
        try:
            with atomic_file_writer(target_path) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["line_number", "field", "reason", "raw_data"],
                    lineterminator="\n",
                )
                writer.writeheader()
                for err in errors:
                    writer.writerow(err.to_dict())
                    count += 1
        except Exception as error:
            raise DataExportError(f"Помилка запису файлу звіту помилок: {error}") from error

        return count


def export_error_report_json(errors: Iterable[InvalidRecordDetail], target_path: Path) -> int:
    """Атомарний експорт відхилених записів у формат JSON."""
    count = 0
    with atomic_file_writer(target_path) as file:
        file.write("[\n")
        first = True
        for err in errors:
            if not first:
                file.write(",\n")
            json.dump(err.to_dict(), file, ensure_ascii=False, indent=2)
            first = False
            count += 1
        file.write("\n]\n")
    return count
