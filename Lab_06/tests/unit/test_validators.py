"""Модульні тести валідації записів та перевірки винятків (RecordValidationError)."""

from datetime import datetime
from typing import Any
import pytest

from sports_accounting.config import AppConfig
from sports_accounting.exceptions import RecordValidationError
from sports_accounting.validators import parse_and_validate_record


class TestRecordValidator:
    """Тести валідації записів спортивних результатів."""

    @pytest.fixture
    def valid_row(self) -> dict[str, Any]:
        return {
            "id": 1,
            "athlete_id": 101,
            "athlete": "Ярослава Магучіх",
            "age": 22,
            "country": "Україна",
            "sport_id": 1,
            "sport": "Стрибки у висоту",
            "unit": "m",
            "is_lower_better": "false",
            "competition_id": 1,
            "competition": "Diamond League",
            "location": "Париж",
            "year": 2024,
            "result": 2.10,
            "category": "Дорослі",
            "timestamp": "2024-07-07T18:30:00",
        }

    def test_parse_valid_row(self, valid_row: dict[str, Any], sample_config: AppConfig) -> None:
        res = parse_and_validate_record(valid_row, line_number=2, config=sample_config)
        assert res.id == 1
        assert res.athlete.name == "Ярослава Магучіх"
        assert res.score.value == pytest.approx(2.10)
        assert res.score.unit == "m"
        assert res.category == "Дорослі"

    def test_invalid_id_raises(self, valid_row: dict[str, Any], sample_config: AppConfig) -> None:
        valid_row["id"] = "not_an_int"
        with pytest.raises(RecordValidationError) as exc_info:
            parse_and_validate_record(valid_row, line_number=5, config=sample_config)
        assert exc_info.value.field == "id"
        assert exc_info.value.line_number == 5
        # Перевірка Exception Chaining: першопричиною є ValueError
        assert isinstance(exc_info.value.__cause__, ValueError)

    def test_negative_id_raises(self, valid_row: dict[str, Any], sample_config: AppConfig) -> None:
        valid_row["id"] = -5
        with pytest.raises(RecordValidationError) as exc_info:
            parse_and_validate_record(valid_row, line_number=6, config=sample_config)
        assert exc_info.value.field == "id"

    def test_empty_athlete_raises(self, valid_row: dict[str, Any], sample_config: AppConfig) -> None:
        valid_row["athlete"] = "   "
        with pytest.raises(RecordValidationError, match="Ім'я спортсмена не може бути порожнім") as exc_info:
            parse_and_validate_record(valid_row, line_number=7, config=sample_config)
        assert exc_info.value.field == "athlete"
        assert exc_info.value.line_number == 7

    def test_invalid_athlete_age_raises(self, valid_row: dict[str, Any], sample_config: AppConfig) -> None:
        valid_row["age"] = "not_a_number"
        with pytest.raises(RecordValidationError) as exc_info:
            parse_and_validate_record(valid_row, line_number=8, config=sample_config)
        assert exc_info.value.field == "age"

    def test_unsupported_sport_raises(self, valid_row: dict[str, Any], sample_config: AppConfig) -> None:
        valid_row["sport"] = "Футбол"
        with pytest.raises(RecordValidationError, match="не входить до списку дозволених") as exc_info:
            parse_and_validate_record(valid_row, line_number=9, config=sample_config)
        assert exc_info.value.field == "sport"
        assert exc_info.value.raw_value == "Футбол"

    def test_non_numeric_result_raises(self, valid_row: dict[str, Any], sample_config: AppConfig) -> None:
        valid_row["result"] = "invalid_score"
        with pytest.raises(RecordValidationError, match="Результат має бути невід'ємним числом") as exc_info:
            parse_and_validate_record(valid_row, line_number=10, config=sample_config)
        assert exc_info.value.field == "result"
        assert isinstance(exc_info.value.__cause__, ValueError)

    @pytest.mark.parametrize(
        ("score", "is_valid"),
        [
            (0.99, False),   # boundary below min_value (1.00)
            (1.00, True),    # boundary exact min
            (2.10, True),    # normal valid
            (2.50, True),    # boundary exact max
            (2.51, False),   # boundary above max_value (2.50)
        ],
        ids=["below_min", "exact_min", "normal_valid", "exact_max", "above_max"],
    )
    def test_score_range_boundaries(
        self,
        valid_row: dict[str, Any],
        sample_config: AppConfig,
        score: float,
        is_valid: bool,
    ) -> None:
        valid_row["result"] = score
        if is_valid:
            res = parse_and_validate_record(valid_row, line_number=11, config=sample_config)
            assert res.score.value == pytest.approx(score)
        else:
            with pytest.raises(RecordValidationError, match="виходить за межі діапазону"):
                parse_and_validate_record(valid_row, line_number=11, config=sample_config)

    def test_unsupported_category_raises(self, valid_row: dict[str, Any], sample_config: AppConfig) -> None:
        valid_row["category"] = "Аматори"
        with pytest.raises(RecordValidationError, match="не підтримується системою") as exc_info:
            parse_and_validate_record(valid_row, line_number=12, config=sample_config)
        assert exc_info.value.field == "category"

    def test_malformed_timestamp_raises(self, valid_row: dict[str, Any], sample_config: AppConfig) -> None:
        valid_row["timestamp"] = "некоректна дата"
        with pytest.raises(RecordValidationError, match="Некоректний формат дати/часу"):
            parse_and_validate_record(valid_row, line_number=13, config=sample_config)

    def test_old_timestamp_raises(self, valid_row: dict[str, Any], sample_config: AppConfig) -> None:
        # min_timestamp in sample_config is 2024-01-01
        valid_row["timestamp"] = "2020-05-10T12:00:00"
        with pytest.raises(RecordValidationError, match="старіша за мінімально дозволену") as exc_info:
            parse_and_validate_record(valid_row, line_number=14, config=sample_config)
        assert exc_info.value.field == "timestamp"
