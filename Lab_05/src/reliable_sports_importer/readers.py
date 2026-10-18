"""Потокові рідери для різних форматів файлів (CSV, JSONL, YAML)."""

from collections.abc import Iterator
import csv
import json
from pathlib import Path
from typing import Any, Protocol
import yaml

from reliable_sports_importer.exceptions import DataImportError


class Importer(Protocol):
    """Структурний протокол (Task 84/85) для імпорту записів у потоковому режимі."""

    def read(self, path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
        """Повертає ітератор кортежів (номер_рядка, словник_даних)."""
        ...


class CsvImporter:
    """Потоковий імпортер для CSV файлів."""

    def read(self, path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
        try:
            with path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames is None:
                    raise DataImportError(f"Файл CSV порожній або не має заголовка: {path}")
                for line_number, row in enumerate(reader, start=2):
                    yield line_number, row
        except OSError as error:
            raise DataImportError(f"Помилка відкриття CSV файлу '{path}': {error}") from error


class JsonLinesImporter:
    """Потоковий імпортер для JSON Lines (JSONL) (Task 86/87)."""

    def read(self, path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
        try:
            with path.open("r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    clean_line = line.strip()
                    if not clean_line:
                        continue
                    try:
                        parsed = json.loads(clean_line)
                        if isinstance(parsed, dict):
                            yield line_number, parsed
                        else:
                            raise DataImportError(f"Рядок {line_number} не є об'єктом JSON")
                    except json.JSONDecodeError as error:
                        raise DataImportError(f"Некоректний JSON на рядку {line_number}: {error}") from error
        except OSError as error:
            raise DataImportError(f"Помилка відкриття JSONL файлу '{path}': {error}") from error


class YamlImporter:
    """Імпортер для списків у форматі YAML."""

    def read(self, path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
        try:
            with path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if not isinstance(data, list):
                    raise DataImportError("YAML документ повинен містити список об'єктів")
                for index, item in enumerate(data, start=1):
                    if isinstance(item, dict):
                        yield index, item
                    else:
                        raise DataImportError(f"Елемент #{index} у YAML не є словником")
        except yaml.YAMLError as error:
            raise DataImportError(f"Помилка синтаксису YAML у '{path}': {error}") from error
        except OSError as error:
            raise DataImportError(f"Помилка читання файлу YAML '{path}': {error}") from error


def get_importer_for_path(path: Path) -> Importer:
    """Автоматичний вибір імплементації за розширенням файлу (Task 84.4)."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return CsvImporter()
    if suffix in (".jsonl", ".ndjson"):
        return JsonLinesImporter()
    if suffix in (".yaml", ".yml"):
        return YamlImporter()
    # За замовчуванням CSV
    return CsvImporter()
