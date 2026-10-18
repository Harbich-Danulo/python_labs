"""Налаштування логування для консолі та файлу з безпекою чутливих даних."""

import logging
from pathlib import Path


def configure_logging(level: str, path: Path) -> None:
    """Ініціалізує root logger із файловим та консольним обробниками."""
    path.parent.mkdir(parents=True, exist_ok=True)

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    file_handler = logging.FileHandler(path, encoding="utf-8")
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
