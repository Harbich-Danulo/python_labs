"""Завантаження та валідація конфігурації YAML із підтримкою змінних середовища."""

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
from typing import Any
import yaml

from sports_accounting.exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class SportRuleConfig:
    """Правило допустимих меж результату для спортивної дисципліни."""

    min_value: float
    max_value: float


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Конфігурація додатку обліку результатів."""

    input_path: Path
    output_path: Path
    allowed_sports: tuple[str, ...]
    allowed_categories: tuple[str, ...]
    sport_rules: dict[str, SportRuleConfig]
    min_timestamp: datetime | None
    env_mode: str
    log_level: str


def load_config(path: Path) -> AppConfig:
    """Завантажує конфігурацію за принципом fail-fast з урахуванням змінних середовища."""
    if not path.exists():
        raise ConfigurationError(f"Конфігураційний файл не знайдено: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            raw: Any = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Синтаксична помилка у файлі YAML: {error}") from error
    except OSError as error:
        raise ConfigurationError(f"Помилка читання файлу конфігурації: {error}") from error

    if not isinstance(raw, dict):
        raise ConfigurationError("Кореневий вміст файлу конфігурації має бути словником (YAML mapping)")

    try:
        input_path = Path(str(raw["input"]["path"]))
        output_path = Path(str(raw["output"]["path"]))

        proc = raw["processing"]
        allowed_sports = tuple(str(s) for s in proc.get("allowed_sports", []))
        allowed_categories = tuple(str(c) for c in proc.get("allowed_categories", []))

        rules_raw = proc.get("sport_rules", {})
        sport_rules: dict[str, SportRuleConfig] = {}
        for sport_name, r in rules_raw.items():
            sport_rules[str(sport_name)] = SportRuleConfig(
                min_value=float(r["min_value"]),
                max_value=float(r["max_value"]),
            )

        min_ts_str = proc.get("min_timestamp")
        min_timestamp = datetime.fromisoformat(str(min_ts_str)) if min_ts_str else None

        # Підтримка змінних середовища для перекриття режиму та рівня логування
        env_mode = os.getenv("APP_ENV", raw.get("env_mode", "development"))
        log_level = os.getenv("SPORTS_LOG_LEVEL", raw.get("logging", {}).get("level", "INFO"))

        config = AppConfig(
            input_path=input_path,
            output_path=output_path,
            allowed_sports=allowed_sports,
            allowed_categories=allowed_categories,
            sport_rules=sport_rules,
            min_timestamp=min_timestamp,
            env_mode=env_mode,
            log_level=log_level,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ConfigurationError(f"Некоректна структура конфігурації: {error}") from error

    validate_config(config)
    return config


def validate_config(config: AppConfig) -> None:
    """Семантична валідація параметрів конфігурації."""
    if not config.allowed_sports:
        raise ConfigurationError("Список дозволених видів спорту (allowed_sports) не може бути порожнім")
    if not config.allowed_categories:
        raise ConfigurationError("Список дозволених категорій (allowed_categories) не може бути порожнім")

    for sport_name, rule in config.sport_rules.items():
        if rule.min_value > rule.max_value:
            raise ConfigurationError(
                f"Некоректний діапазон для '{sport_name}': min_value ({rule.min_value}) > max_value ({rule.max_value})"
            )
