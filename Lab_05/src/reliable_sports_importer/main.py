"""Точка входу в програму надійного імпорту та експорту спортивних результатів."""

import logging
from pathlib import Path
import sys

from reliable_sports_importer.config import load_config
from reliable_sports_importer.exceptions import ApplicationError
from reliable_sports_importer.logging_config import configure_logging
from reliable_sports_importer.services import SportsProcessingService
from reliable_sports_importer.utils import logged_operation

logger = logging.getLogger("reliable_sports_importer.main")


def main() -> None:
    """Головна функція виконання додатку."""
    config_path = Path("config.yaml")

    try:
        # 1. Завантаження конфігурації
        config = load_config(config_path)

        # 2. Налаштування логування
        configure_logging(config.logging.level, config.logging.path)

        logger.info("=" * 65)
        logger.info("ЛАБОРАТОРНА РОБОТА №5: ОБРОБКА ПОМИЛОК, ФАЙЛИ ТА СЕРІАЛІЗАЦІЯ")
        logger.info("Варіант 9: Імпорт та експорт спортивних результатів")
        logger.info("Конфігурацію успішно завантажено з: %s", config_path)
        logger.info("Режим обробки: %s", "Tolerant (skip_invalid=True)" if config.processing.skip_invalid else "Strict (skip_invalid=False)")
        logger.info("=" * 65)

        # 3. Запуск конвеєра в контекстному менеджері вимірювання часу
        service = SportsProcessingService(config)

        with logged_operation("Sports Data Pipeline Processing"):
            stats = service.run_pipeline()

        logger.info("-" * 65)
        logger.info("ПІДСУМКОВА СТАТИСТИКА ВИКОНАННЯ:")
        logger.info("  Всього прочитано записів: %d", stats.total_records)
        logger.info("  Валідних записів (успішно): %d", stats.valid_records)
        logger.info("  Некоректних записів (помилки): %d", stats.invalid_records)
        logger.info("  Експортовано у %s: %d", config.output_path, stats.exported_records)
        if stats.invalid_records > 0:
            logger.info("  Окремий звіт про помилки записано у: %s", config.error_report_path)
        logger.info("-" * 65)

    except ApplicationError as error:
        # Контрольоване завершення при доменних помилках
        logger.error("Критична помилка виконання додатку: %s", error)
        print(f"\n[CRITICAL APPLICATION ERROR]: {error}", file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        # Непередбачуваний збій
        logger.exception("Непередбачена критична системна помилка: %s", error)
        print(f"\n[UNEXPECTED SYSTEM ERROR]: {error}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
