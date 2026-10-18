"""Валідація та перетворення вхідних рядків у доменні моделі SportsResult."""

from datetime import datetime
from typing import Any

from reliable_sports_importer.exceptions import RecordValidationError
from reliable_sports_importer.models import ProcessingConfig, SportsResult


def parse_and_validate_record(
    row: dict[str, Any],
    *,
    line_number: int,
    config: ProcessingConfig,
) -> SportsResult:
    """Парсить словник значень та валідує бізнес-правила (Варіант 9)."""
    # 1. Валідація спортсмена (athlete)
    athlete_raw = str(row.get("athlete", "")).strip()
    if not athlete_raw:
        raise RecordValidationError(
            "Ім'я спортсмена не може бути порожнім",
            line_number=line_number,
            field="athlete",
            raw_value=row.get("athlete"),
        )

    # 2. Валідація виду спорту (sport)
    sport_raw = str(row.get("sport", "")).strip()
    if not sport_raw:
        raise RecordValidationError(
            "Назва виду спорту відсутня",
            line_number=line_number,
            field="sport",
            raw_value=row.get("sport"),
        )
    if config.allowed_sports and sport_raw not in config.allowed_sports:
        raise RecordValidationError(
            f"Вид спорту '{sport_raw}' не входить до переліку дозволених {config.allowed_sports}",
            line_number=line_number,
            field="sport",
            raw_value=sport_raw,
        )

    # 3. Валідація числового результату (result)
    result_raw = row.get("result")
    try:
        result_val = float(result_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise RecordValidationError(
            f"Результат має бути дійсним числовим значенням: {result_raw}",
            line_number=line_number,
            field="result",
            raw_value=result_raw,
        ) from error

    # Перевірка діапазонів із конфігурації
    rule = config.sport_rules.get(sport_raw)
    if rule:
        if result_val < rule.min_value or result_val > rule.max_value:
            raise RecordValidationError(
                f"Результат {result_val} виходить за межі допустимого діапазону [{rule.min_value}, {rule.max_value}] для виду спорту '{sport_raw}'",
                line_number=line_number,
                field="result",
                raw_value=result_val,
            )

    # 4. Валідація категорії (category)
    category_raw = str(row.get("category", "")).strip()
    if not category_raw:
        raise RecordValidationError(
            "Категорія змагань не може бути порожньою",
            line_number=line_number,
            field="category",
            raw_value=row.get("category"),
        )
    if config.allowed_categories and category_raw not in config.allowed_categories:
        raise RecordValidationError(
            f"Категорія '{category_raw}' не підтримується системою",
            line_number=line_number,
            field="category",
            raw_value=category_raw,
        )

    # 5. Валідація часової мітки (timestamp)
    ts_raw = row.get("timestamp")
    try:
        if isinstance(ts_raw, datetime):
            parsed_timestamp = ts_raw
        else:
            parsed_timestamp = datetime.fromisoformat(str(ts_raw).strip())
    except (TypeError, ValueError) as error:
        raise RecordValidationError(
            f"Некоректний формат дати/часу (очікується ISO 8601 YYYY-MM-DDTHH:MM:SS): {ts_raw}",
            line_number=line_number,
            field="timestamp",
            raw_value=ts_raw,
        ) from error

    if config.min_timestamp and parsed_timestamp < config.min_timestamp:
        raise RecordValidationError(
            f"Часова мітка {parsed_timestamp} є старішою за мінімально дозволену {config.min_timestamp}",
            line_number=line_number,
            field="timestamp",
            raw_value=parsed_timestamp.isoformat(),
        )

    return SportsResult(
        athlete=athlete_raw,
        sport=sport_raw,
        result=result_val,
        category=category_raw,
        timestamp=parsed_timestamp,
    )
