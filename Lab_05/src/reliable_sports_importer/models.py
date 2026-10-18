"""Доменні сутності та моделі конфігурації."""

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class SportsResult:
    """Доменна сутність спортивного результату (Варіант 9)."""

    athlete: str
    sport: str
    result: float
    category: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        """Серіалізація сутності в словник для експорту."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass(frozen=True, slots=True)
class InvalidRecordDetail:
    """Інформація про відхилений запис для error report."""

    line_number: int
    raw_data: str
    reason: str
    field: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SportRuleConfig:
    """Правило валідації діапазону значень для конкретного виду спорту."""

    min_value: float
    max_value: float


@dataclass(frozen=True, slots=True)
class ProcessingConfig:
    """Параметри обробки даних."""

    skip_invalid: bool
    allowed_categories: tuple[str, ...]
    allowed_sports: tuple[str, ...]
    sport_rules: dict[str, SportRuleConfig]
    min_timestamp: datetime | None = None


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    """Параметри журналювання."""

    level: str
    path: Path


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Загальна конфігурація додатку."""

    input_path: Path
    output_path: Path
    error_report_path: Path
    processing: ProcessingConfig
    logging: LoggingConfig
