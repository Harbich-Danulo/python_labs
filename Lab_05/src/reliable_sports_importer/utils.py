"""Контекстні менеджери для транзакційного виконання та профілювання."""

from collections.abc import Iterator
from contextlib import contextmanager
import logging
from pathlib import Path
from time import perf_counter
from typing import Any

from reliable_sports_importer.exceptions import DataExportError

logger = logging.getLogger(__name__)


@contextmanager
def logged_operation(operation_name: str) -> Iterator[None]:
    """Власний контекст-менеджер із вимірюванням часу та протоколюванням подій."""
    logger.info("Початок операції: %s", operation_name)
    start_time = perf_counter()
    try:
        yield
    except Exception as error:
        elapsed = perf_counter() - start_time
        logger.exception("Операція '%s' зазнала аварійного збою після %.6f с: %s", operation_name, elapsed, error)
        raise
    else:
        elapsed = perf_counter() - start_time
        logger.info("Операція '%s' успішно завершена за %.6f с", operation_name, elapsed)


@contextmanager
def atomic_file_writer(target_path: Path, encoding: str = "utf-8") -> Iterator[Any]:
    """Контекстний менеджер атомарного запису: пише у *.tmp і перейменовує лише у разі успіху."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target_path.with_suffix(target_path.suffix + ".tmp")

    try:
        with temp_path.open("w", encoding=encoding) as file:
            yield file
        # Якщо блок with завершився без помилок, атомарно замінюємо цільовий файл
        temp_path.replace(target_path)
    except Exception as error:
        # У разі будь-якого винятку очищуємо тимчасовий файл
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise DataExportError(f"Неможливо виконати атомарний запис у {target_path}: {error}") from error
