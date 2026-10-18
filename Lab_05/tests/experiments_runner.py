"""Скрипт виконання всіх 5 експериментів для Лабораторної роботи №5."""

from collections.abc import Iterator
import csv
from datetime import datetime
import json
from pathlib import Path
import sys
import time
import tracemalloc
from typing import Any
import yaml

from reliable_sports_importer.config import load_config
from reliable_sports_importer.exceptions import (
    ApplicationError,
    ConfigurationError,
    DataExportError,
    RecordValidationError,
)
from reliable_sports_importer.exporters import JsonStreamExporter
from reliable_sports_importer.models import AppConfig, ProcessingConfig, SportsResult
from reliable_sports_importer.services import SportsProcessingService
from reliable_sports_importer.utils import atomic_file_writer
from reliable_sports_importer.validators import parse_and_validate_record


def run_experiment_1() -> dict[str, Any]:
    """Експеримент 1: Порівняння Strict vs Tolerant mode на 1000 valid + 10 invalid."""
    print("\n--- Експеримент 1: Strict vs Tolerant mode ---")
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    exp1_file = data_dir / "exp1_dataset.csv"

    # Генеруємо 1000 валідних + 10 невалідних
    with exp1_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["athlete", "sport", "result", "category", "timestamp"])
        for i in range(1, 1001):
            writer.writerow([f"Athlete_{i}", "Стрибки у висоту", "2.10", "Дорослі", "2024-05-01T12:00:00"])
        for j in range(1, 11):
            writer.writerow([f"InvalidAthlete_{j}", "Стрибки у висоту", "99.99", "Дорослі", "2024-05-01T12:00:00"])

    base_config = load_config(Path("config.yaml"))

    # 1. Strict mode
    strict_processing = ProcessingConfig(
        skip_invalid=False,
        allowed_categories=base_config.processing.allowed_categories,
        allowed_sports=base_config.processing.allowed_sports,
        sport_rules=base_config.processing.sport_rules,
        min_timestamp=base_config.processing.min_timestamp,
    )
    strict_config = AppConfig(
        input_path=exp1_file,
        output_path=Path("output/exp1_strict.json"),
        error_report_path=Path("output/exp1_strict_errors.json"),
        processing=strict_processing,
        logging=base_config.logging,
    )

    strict_service = SportsProcessingService(strict_config)
    strict_status = "Перервано винятком (RecordValidationError)"
    try:
        strict_service.run_pipeline()
        strict_status = "Успішно"
    except (RecordValidationError, DataExportError):
        pass

    # 2. Tolerant mode
    tolerant_processing = ProcessingConfig(
        skip_invalid=True,
        allowed_categories=base_config.processing.allowed_categories,
        allowed_sports=base_config.processing.allowed_sports,
        sport_rules=base_config.processing.sport_rules,
        min_timestamp=base_config.processing.min_timestamp,
    )
    tolerant_config = AppConfig(
        input_path=exp1_file,
        output_path=Path("output/exp1_tolerant.json"),
        error_report_path=Path("output/exp1_tolerant_errors.json"),
        processing=tolerant_processing,
        logging=base_config.logging,
    )
    tolerant_service = SportsProcessingService(tolerant_config)
    tolerant_service.run_pipeline()
    tolerant_status = "Успішно (помилки пропущені)"

    results = {
        "strict": {
            "total": strict_service.statistics.total_records,
            "valid": strict_service.statistics.valid_records,
            "invalid": strict_service.statistics.invalid_records,
            "exported": strict_service.statistics.exported_records,
            "status": strict_status,
        },
        "tolerant": {
            "total": tolerant_service.statistics.total_records,
            "valid": tolerant_service.statistics.valid_records,
            "invalid": tolerant_service.statistics.invalid_records,
            "exported": tolerant_service.statistics.exported_records,
            "status": tolerant_status,
        },
    }
    print(f"Strict:   {results['strict']}")
    print(f"Tolerant: {results['tolerant']}")
    return results


def run_experiment_2() -> list[dict[str, Any]]:
    """Експеримент 2: Streaming vs Eager (10_000, 100_000, 500_000 записів)."""
    print("\n--- Експеримент 2: Streaming vs Eager ---")
    data_dir = Path("data")
    sizes = [10_000, 100_000, 500_000]
    table_data = []

    for count in sizes:
        csv_file = data_dir / f"benchmark_{count}.csv"
        print(f"Генерація CSV файлу на {count} рядків...")
        with csv_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["athlete", "sport", "result", "category", "timestamp"])
            for i in range(1, count + 1):
                writer.writerow([f"Athlete_{i}", "Стрибки у висоту", "2.05", "Дорослі", "2024-05-01T12:00:00"])

        # Eager variant
        def eager_import(path: Path) -> list[dict[str, str]]:
            with path.open("r", encoding="utf-8", newline="") as file:
                return list(csv.DictReader(file))

        # Streaming variant
        def streaming_import(path: Path) -> Iterator[dict[str, str]]:
            with path.open("r", encoding="utf-8", newline="") as file:
                yield from csv.DictReader(file)

        # Тест Eager
        tracemalloc.start()
        start_time = time.perf_counter()
        eager_records = eager_import(csv_file)
        # Прохід для еквівалентності
        _ = len(eager_records)
        eager_time = time.perf_counter() - start_time
        _, eager_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        eager_peak_mb = eager_peak / (1024 * 1024)

        # Очищуємо пам'ять
        del eager_records

        # Тест Streaming
        tracemalloc.start()
        start_time = time.perf_counter()
        stream_count = 0
        for _ in streaming_import(csv_file):
            stream_count += 1
        streaming_time = time.perf_counter() - start_time
        _, stream_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        stream_peak_mb = stream_peak / (1024 * 1024)

        row_info = {
            "records": count,
            "eager_time": round(eager_time, 4),
            "streaming_time": round(streaming_time, 4),
            "eager_peak_mb": round(eager_peak_mb, 2),
            "streaming_peak_mb": round(stream_peak_mb, 4),
        }
        table_data.append(row_info)
        print(f"Records: {count:>7} | Eager: {eager_time:.4f}s ({eager_peak_mb:.2f} MB) | Stream: {streaming_time:.4f}s ({stream_peak_mb:.4f} MB)")

        # Видаляємо тестові великі файли щоб не засмічувати диск
        try:
            csv_file.unlink(missing_ok=True)
        except OSError:
            pass

    return table_data


def run_experiment_3() -> str:
    """Експеримент 3: Демонстрація Exception Chaining (ValueError -> RecordValidationError)."""
    print("\n--- Експеримент 3: Exception Chaining ---")
    bad_row = {
        "athlete": "Ярослава Магучіх",
        "sport": "Стрибки у висоту",
        "result": "not_a_number",
        "category": "Дорослі",
        "timestamp": "2024-07-07T18:30:00",
    }
    dummy_cfg = ProcessingConfig(
        skip_invalid=False,
        allowed_categories=("Дорослі",),
        allowed_sports=("Стрибки у висоту",),
        sport_rules={},
    )

    import traceback
    chain_trace = ""
    try:
        parse_and_validate_record(bad_row, line_number=42, config=dummy_cfg)
    except RecordValidationError as exc:
        chain_trace = "".join(traceback.format_exception(exc))
        print("Отримано очікуваний ланцюжок винятків:")
        print(chain_trace)
    return chain_trace


def run_experiment_4() -> bool:
    """Експеримент 4: Атомарний запис (Atomic Output)."""
    print("\n--- Експеримент 4: Atomic Output ---")
    target_file = Path("output/atomic_test_production.json")
    target_file.parent.mkdir(exist_ok=True)

    # 1. Записуємо початковий валідний файл
    initial_content = '[{"status": "INITIAL_VALID_DATA"}]\n'
    target_file.write_text(initial_content, encoding="utf-8")

    # 2. Спробуємо виконати запис, у якому виникне помилка всередині блоку
    temp_file = target_file.with_suffix(target_file.suffix + ".tmp")
    threw_error = False
    try:
        with atomic_file_writer(target_file) as f:
            f.write('[{"status": "PARTIAL_BROKEN_DATA"')
            raise RuntimeError("Симуляція аварійного завершення живлення або I/O збою!")
    except DataExportError:
        threw_error = True

    # 3. Перевіряємо інваріанти
    current_content = target_file.read_text(encoding="utf-8")
    is_valid_preserved = (current_content == initial_content)
    is_temp_cleaned = not temp_file.exists()

    print(f"Помилка була перехоплена і загорнута в DataExportError: {threw_error}")
    print(f"Попередній робочий файл збережено без спотворень: {is_valid_preserved}")
    print(f"Тимчасовий *.tmp файл успішно видалено з файлової системи: {is_temp_cleaned}")
    return is_valid_preserved and is_temp_cleaned


def run_experiment_5() -> list[dict[str, str]]:
    """Експеримент 5: Тестування 6 сценаріїв некоректної конфігурації (Fail-fast)."""
    print("\n--- Експеримент 5: Configuration Errors ---")
    scenarios = [
        {"name": "1. Відсутній config.yaml", "path": Path("config_non_existent.yaml"), "action": "load"},
        {"name": "2. Неправильний синтаксис YAML", "content": "input:\n  path: [unclosed_list", "action": "parse"},
        {"name": "3. Немає секції input", "content": "output:\n  path: out.json\nprocessing:\n  skip_invalid: true\nlogging:\n  level: INFO", "action": "parse"},
        {"name": "4. Некоректне правило min_value > max_value", "content": "input:\n  path: data/sports_results.csv\noutput:\n  path: out.json\nprocessing:\n  allowed_sports: ['Стрибки']\n  allowed_categories: ['Дорослі']\n  sport_rules:\n    'Стрибки':\n      min_value: 300\n      max_value: 10\nlogging:\n  level: INFO", "action": "parse"},
        {"name": "5. Вхідний файл відсутній на диску", "content": "input:\n  path: missing_file.csv\noutput:\n  path: out.json\nprocessing:\n  allowed_sports: ['Стрибки']\n  allowed_categories: ['Дорослі']\nlogging:\n  level: INFO", "action": "parse"},
        {"name": "6. Порожній список дозволених видів спорту", "content": "input:\n  path: data/sports_results.csv\noutput:\n  path: out.json\nprocessing:\n  allowed_sports: []\n  allowed_categories: ['Дорослі']\nlogging:\n  level: INFO", "action": "parse"},
    ]

    results = []
    tmp_cfg_file = Path("temp_test_config.yaml")

    for sc in scenarios:
        err_msg = ""
        try:
            if sc["action"] == "load":
                load_config(sc["path"])
            else:
                tmp_cfg_file.write_text(sc["content"], encoding="utf-8")
                load_config(tmp_cfg_file)
            err_msg = "ПОМИЛКА: Валідатор пропустив некоректний конфіг!"
        except ConfigurationError as exc:
            err_msg = f"ConfigurationError: {exc}"
        except Exception as exc:
            err_msg = f"Unexpected exception: {type(exc).__name__}: {exc}"

        print(f"Сценарій '{sc['name']}': {err_msg}")
        results.append({"scenario": sc["name"], "result": err_msg})

    tmp_cfg_file.unlink(missing_ok=True)
    return results


if __name__ == "__main__":
    print("=== ЗАПУСК ПОВНОГО КОМПЛЕКСУ ЕКСПЕРИМЕНТІВ ЛАБОРАТОРНОЇ РОБОТИ №5 ===")
    exp1_res = run_experiment_1()
    exp2_res = run_experiment_2()
    exp3_res = run_experiment_3()
    exp4_res = run_experiment_4()
    exp5_res = run_experiment_5()
    print("\nУсі експерименти успішно проведено!")
