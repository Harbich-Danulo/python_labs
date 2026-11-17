"""Модуль атомарного експорту результатів у JSON."""

from collections.abc import Iterable, Iterator
from contextlib import contextmanager
import json
from pathlib import Path
from typing import Any

from sports_accounting.exceptions import DataExportError
from sports_accounting.models import Result
from sports_accounting.protocols import ResultExporter


@contextmanager
def atomic_file_writer(target_path: Path, encoding: str = "utf-8") -> Iterator[Any]:
    """Контекстний менеджер для атомарного запису: пише у *.tmp і перейменовує лише при успіху."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target_path.with_suffix(target_path.suffix + ".tmp")

    try:
        with temp_path.open("w", encoding=encoding) as file:
            yield file
        temp_path.replace(target_path)
    except Exception as error:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise DataExportError(f"Аварійний збій атомарного запису у '{target_path}': {error}") from error


class JsonResultExporter(ResultExporter):
    """Атомарний експортер результатів у валідний масив JSON."""

    def export(self, results: Iterable[Result], target_path: Path) -> int:
        count = 0
        try:
            with atomic_file_writer(target_path) as file:
                file.write("[\n")
                first = True
                for res in results:
                    if not first:
                        file.write(",\n")
                    json.dump(res.to_dict(), file, ensure_ascii=False, indent=2)
                    first = False
                    count += 1
                file.write("\n]\n")
        except DataExportError:
            raise
        except Exception as error:
            raise DataExportError(f"Помилка формування JSON-файлу '{target_path}': {error}") from error

        return count
