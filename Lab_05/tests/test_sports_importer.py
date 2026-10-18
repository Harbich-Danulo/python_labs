"""Модульні тести для надійного імпортера спортивних результатів."""

from datetime import datetime
from pathlib import Path
import unittest

from reliable_sports_importer.config import load_config
from reliable_sports_importer.exceptions import (
    ConfigurationError,
    DataExportError,
    RecordValidationError,
)
from reliable_sports_importer.exporters import JsonStreamExporter
from reliable_sports_importer.models import AppConfig, ProcessingConfig, SportRuleConfig, SportsResult
from reliable_sports_importer.services import SportsProcessingService
from reliable_sports_importer.utils import atomic_file_writer
from reliable_sports_importer.validators import parse_and_validate_record


class TestReliableSportsImporter(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProcessingConfig(
            skip_invalid=True,
            allowed_categories=("Дорослі", "Юніори"),
            allowed_sports=("Стрибки у висоту", "Плавання 800м"),
            sport_rules={
                "Стрибки у висоту": SportRuleConfig(min_value=1.0, max_value=2.5),
                "Плавання 800м": SportRuleConfig(min_value=400.0, max_value=800.0),
            },
            min_timestamp=datetime(2024, 1, 1),
        )

    def test_valid_record_parsing(self) -> None:
        raw = {
            "athlete": "Ярослава Магучіх",
            "sport": "Стрибки у висоту",
            "result": "2.10",
            "category": "Дорослі",
            "timestamp": "2024-07-07T18:30:00",
        }
        res = parse_and_validate_record(raw, line_number=2, config=self.config)
        self.assertEqual(res.athlete, "Ярослава Магучіх")
        self.assertEqual(res.result, 2.10)
        self.assertEqual(res.category, "Дорослі")

    def test_invalid_athlete_name(self) -> None:
        raw = {
            "athlete": "   ",
            "sport": "Стрибки у висоту",
            "result": "2.10",
            "category": "Дорослі",
            "timestamp": "2024-07-07T18:30:00",
        }
        with self.assertRaises(RecordValidationError) as ctx:
            parse_and_validate_record(raw, line_number=3, config=self.config)
        self.assertEqual(ctx.exception.field, "athlete")

    def test_out_of_bounds_result(self) -> None:
        raw = {
            "athlete": "Сергій Бубка",
            "sport": "Стрибки у висоту",
            "result": "3.50",
            "category": "Дорослі",
            "timestamp": "2024-07-07T18:30:00",
        }
        with self.assertRaises(RecordValidationError) as ctx:
            parse_and_validate_record(raw, line_number=4, config=self.config)
        self.assertEqual(ctx.exception.field, "result")

    def test_unsupported_sport(self) -> None:
        raw = {
            "athlete": "Гравець",
            "sport": "Футбол",
            "result": "3.0",
            "category": "Дорослі",
            "timestamp": "2024-07-07T18:30:00",
        }
        with self.assertRaises(RecordValidationError) as ctx:
            parse_and_validate_record(raw, line_number=5, config=self.config)
        self.assertEqual(ctx.exception.field, "sport")

    def test_atomic_writer_cleanup_on_error(self) -> None:
        out_path = Path("output/test_atomic_cleanup.json")
        out_path.parent.mkdir(exist_ok=True)
        temp_path = out_path.with_suffix(out_path.suffix + ".tmp")

        with self.assertRaises(DataExportError):
            with atomic_file_writer(out_path) as f:
                f.write("Broken data")
                raise ValueError("Crash")

        self.assertFalse(temp_path.exists())
        self.assertFalse(out_path.exists())


if __name__ == "__main__":
    unittest.main()
