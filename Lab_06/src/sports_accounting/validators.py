"""Модуль валідації та перетворення даних у доменні сутності."""

from datetime import datetime
from typing import Any

from sports_accounting.config import AppConfig
from sports_accounting.exceptions import RecordValidationError
from sports_accounting.models import Athlete, Competition, Result, Sport
from sports_accounting.value_objects import Score


def parse_and_validate_record(
    row: dict[str, Any],
    *,
    line_number: int,
    config: AppConfig,
) -> Result:
    """Парсить та валідує словник даних спортивного результату."""
    # 1. Валідація ID результату
    raw_id = row.get("id")
    try:
        res_id = int(str(raw_id))
        if res_id <= 0:
            raise ValueError(f"ID має бути додатнім числом: {res_id}")
    except (TypeError, ValueError) as error:
        raise RecordValidationError(
            f"Некоректний ID результату: {raw_id}",
            line_number=line_number,
            field="id",
            raw_value=raw_id,
        ) from error

    # 2. Валідація спортсмена
    athlete_name = str(row.get("athlete", "")).strip()
    if not athlete_name:
        raise RecordValidationError(
            "Ім'я спортсмена не може бути порожнім",
            line_number=line_number,
            field="athlete",
            raw_value=row.get("athlete"),
        )

    try:
        athlete_age = int(str(row.get("age", 25)))
        if not (10 <= athlete_age <= 100):
            raise ValueError(f"Вік спортсмена поза межами [10, 100]: {athlete_age}")
    except (TypeError, ValueError) as error:
        raise RecordValidationError(
            f"Некоректний вік спортсмена: {row.get('age')}",
            line_number=line_number,
            field="age",
            raw_value=row.get("age"),
        ) from error

    athlete = Athlete(
        id=int(str(row.get("athlete_id", res_id))),
        name=athlete_name,
        country=str(row.get("country", "Україна")).strip() or "Україна",
        age=athlete_age,
    )

    # 3. Валідація виду спорту
    sport_name = str(row.get("sport", "")).strip()
    if not sport_name:
        raise RecordValidationError(
            "Вид спорту не може бути порожнім",
            line_number=line_number,
            field="sport",
            raw_value=row.get("sport"),
        )
    if config.allowed_sports and sport_name not in config.allowed_sports:
        raise RecordValidationError(
            f"Вид спорту '{sport_name}' не входить до списку дозволених {config.allowed_sports}",
            line_number=line_number,
            field="sport",
            raw_value=sport_name,
        )

    unit = str(row.get("unit", "m")).strip() or "m"
    is_lower = str(row.get("is_lower_better", "false")).lower() in ("true", "1", "yes")
    sport = Sport(
        id=int(str(row.get("sport_id", 1))),
        name=sport_name,
        unit=unit,
        is_lower_better=is_lower,
    )

    # 4. Валідація результату (Score)
    raw_score = row.get("result")
    try:
        score_val = float(str(raw_score))
        if score_val < 0:
            raise ValueError(f"Результат не може бути від'ємним: {score_val}")
    except (TypeError, ValueError) as error:
        raise RecordValidationError(
            f"Результат має бути невід'ємним числом: {raw_score}",
            line_number=line_number,
            field="result",
            raw_value=raw_score,
        ) from error

    # Перевірка діапазону дисципліни
    rule = config.sport_rules.get(sport_name)
    if rule:
        if score_val < rule.min_value or score_val > rule.max_value:
            raise RecordValidationError(
                f"Результат {score_val} виходить за межі діапазону [{rule.min_value}, {rule.max_value}] для '{sport_name}'",
                line_number=line_number,
                field="result",
                raw_value=score_val,
            )

    score = Score(value=score_val, unit=unit)

    # 5. Валідація змагання
    comp_name = str(row.get("competition", "Чемпіонат України")).strip() or "Чемпіонат України"
    comp_loc = str(row.get("location", "Київ")).strip() or "Київ"
    comp_year = int(str(row.get("year", 2024)))
    competition = Competition(
        id=int(str(row.get("competition_id", 1))),
        name=comp_name,
        location=comp_loc,
        year=comp_year,
    )

    # 6. Валідація категорії
    category = str(row.get("category", "")).strip()
    if not category:
        raise RecordValidationError(
            "Категорія не може бути порожньою",
            line_number=line_number,
            field="category",
            raw_value=row.get("category"),
        )
    if config.allowed_categories and category not in config.allowed_categories:
        raise RecordValidationError(
            f"Категорія '{category}' не підтримується системою",
            line_number=line_number,
            field="category",
            raw_value=category,
        )

    # 7. Валідація часової мітки
    raw_ts = row.get("timestamp")
    try:
        if isinstance(raw_ts, datetime):
            parsed_ts = raw_ts
        else:
            parsed_ts = datetime.fromisoformat(str(raw_ts).strip())
    except (TypeError, ValueError) as error:
        raise RecordValidationError(
            f"Некоректний формат дати/часу (очікується ISO 8601): {raw_ts}",
            line_number=line_number,
            field="timestamp",
            raw_value=raw_ts,
        ) from error

    if config.min_timestamp and parsed_ts < config.min_timestamp:
        raise RecordValidationError(
            f"Дата {parsed_ts} старіша за мінімально дозволену {config.min_timestamp}",
            line_number=line_number,
            field="timestamp",
            raw_value=parsed_ts.isoformat(),
        )

    return Result(
        id=res_id,
        athlete=athlete,
        sport=sport,
        competition=competition,
        score=score,
        category=category,
        timestamp=parsed_ts,
    )
