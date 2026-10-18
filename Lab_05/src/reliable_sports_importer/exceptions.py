"""Ієрархія доменних винятків для системи імпорту та експорту."""

from typing import Any


class ApplicationError(Exception):
    """Базовий виняток додатку."""


class ConfigurationError(ApplicationError):
    """Виникає при помилках завантаження або валідації конфігурації."""


class DataError(ApplicationError):
    """Базовий виняток для помилок роботи з даними."""


class DataImportError(DataError):
    """Виникає при неможливості прочитати вхідний файл або критичній помилці парсингу."""


class RecordValidationError(DataError):
    """Виникає при валідації окремого запису предметної області."""

    def __init__(
        self,
        message: str,
        *,
        line_number: int | None = None,
        field: str | None = None,
        raw_value: Any = None,
    ) -> None:
        super().__init__(message)
        self.line_number = line_number
        self.field = field
        self.raw_value = raw_value

    def __str__(self) -> str:
        parts: list[str] = [super().__str__()]
        if self.line_number is not None:
            parts.append(f"рядок {self.line_number}")
        if self.field is not None:
            parts.append(f"поле '{self.field}'")
        if self.raw_value is not None:
            parts.append(f"значення='{self.raw_value}'")
        if len(parts) > 1:
            return f"{parts[0]} ({', '.join(parts[1:])})"
        return parts[0]


class DataExportError(DataError):
    """Виникає при помилках атомарного експорту або серіалізації."""
