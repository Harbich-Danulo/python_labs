"""Завантаження та валідація конфігурації YAML."""

from datetime import datetime
from pathlib import Path
from typing import Any
import yaml

from reliable_sports_importer.exceptions import ConfigurationError
from reliable_sports_importer.models import (
    AppConfig,
    LoggingConfig,
    ProcessingConfig,
    SportRuleConfig,
)


def load_config(path: Path) -> AppConfig:
    """Завантажує та валідує YAML конфігурацію за принципом fail-fast."""
    if not path.exists():
        raise ConfigurationError(f"Конфігураційний файл не знайдено: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            raw: Any = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Синтаксична помилка у YAML конфігурації: {error}") from error
    except OSError as error:
        raise ConfigurationError(f"Неможливо прочитати файл конфігурації: {error}") from error

    if not isinstance(raw, dict):
        raise ConfigurationError("Вміст конфігураційного файлу має бути коректним словником (YAML mapping)")

    try:
        input_section = raw["input"]
        output_section = raw["output"]
        processing_section = raw["processing"]
        logging_section = raw["logging"]

        input_path = Path(str(input_section["path"]))
        output_path = Path(str(output_section["path"]))
        error_report_path = Path(str(output_section.get("error_report_path", "output/errors.json")))

        raw_rules = processing_section.get("sport_rules", {})
        sport_rules: dict[str, SportRuleConfig] = {}
        for sport_name, rule_data in raw_rules.items():
            sport_rules[str(sport_name)] = SportRuleConfig(
                min_value=float(rule_data["min_value"]),
                max_value=float(rule_data["max_value"]),
            )

        min_ts_str = processing_section.get("min_timestamp")
        min_timestamp = datetime.fromisoformat(str(min_ts_str)) if min_ts_str else None

        processing = ProcessingConfig(
            skip_invalid=bool(processing_section.get("skip_invalid", True)),
            allowed_categories=tuple(str(c) for c in processing_section.get("allowed_categories", [])),
            allowed_sports=tuple(str(s) for s in processing_section.get("allowed_sports", [])),
            sport_rules=sport_rules,
            min_timestamp=min_timestamp,
        )

        logging_cfg = LoggingConfig(
            level=str(logging_section.get("level", "INFO")),
            path=Path(str(logging_section.get("path", "logs/application.log"))),
        )

        config = AppConfig(
            input_path=input_path,
            output_path=output_path,
            error_report_path=error_report_path,
            processing=processing,
            logging=logging_cfg,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ConfigurationError(f"Некоректна структура конфігурації: {error}") from error

    validate_config(config)
    return config


def validate_config(config: AppConfig) -> None:
    """Семантична перевірка значень конфігурації (Fail-fast)."""
    if not config.input_path.exists():
        raise ConfigurationError(f"Вхідний файл для обробки не знайдено: {config.input_path}")

    if not config.processing.allowed_sports:
        raise ConfigurationError("Список дозволених видів спорту (allowed_sports) не може бути порожнім")

    if not config.processing.allowed_categories:
        raise ConfigurationError("Список дозволених категорій (allowed_categories) не може бути порожнім")

    for sport_name, rule in config.processing.sport_rules.items():
        if rule.min_value > rule.max_value:
            raise ConfigurationError(
                f"Некоректне правило для '{sport_name}': min_value ({rule.min_value}) > max_value ({rule.max_value})"
            )
