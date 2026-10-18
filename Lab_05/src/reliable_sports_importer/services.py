"""Сервіс координації конвеєра імпорту, фільтрації, статистики та експорту."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
import logging
from pathlib import Path

from reliable_sports_importer.exceptions import RecordValidationError
from reliable_sports_importer.exporters import (
    CsvErrorExporter,
    JsonStreamExporter,
    export_error_report_json,
)
from reliable_sports_importer.models import (
    AppConfig,
    InvalidRecordDetail,
    SportsResult,
)
from reliable_sports_importer.readers import get_importer_for_path
from reliable_sports_importer.validators import parse_and_validate_record

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStatistics:
    """Статистика обробки записів."""

    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    exported_records: int = 0


class SportsProcessingService:
    """Сервіс керування надійним конвеєром обробки спортивних результатів."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.statistics = ProcessingStatistics()
        self.invalid_records: list[InvalidRecordDetail] = []
        self._json_exporter = JsonStreamExporter()
        self._csv_error_exporter = CsvErrorExporter()

    def stream_valid_results(self) -> Iterator[SportsResult]:
        """Потоковий генератор: читає, валідує і повертає тільки валідні сутності."""
        importer = get_importer_for_path(self.config.input_path)

        for line_number, raw_row in importer.read(self.config.input_path):
            self.statistics.total_records += 1
            try:
                sports_result = parse_and_validate_record(
                    raw_row,
                    line_number=line_number,
                    config=self.config.processing,
                )
            except RecordValidationError as error:
                self.statistics.invalid_records += 1
                detail = InvalidRecordDetail(
                    line_number=line_number,
                    raw_data=str(raw_row),
                    reason=str(error),
                    field=error.field,
                )
                self.invalid_records.append(detail)
                logger.warning("Некоректний запис на рядку %s: %s", line_number, error)

                if self.config.processing.skip_invalid:
                    continue  # Tolerant mode
                # Strict mode: перериваємо обробку
                raise

            self.statistics.valid_records += 1
            yield sports_result

    def filter_results(self, results: Iterable[SportsResult]) -> Iterator[SportsResult]:
        """Фільтрація за додатковими критеріями (бізнес-обробка)."""
        for item in results:
            # Наприклад, пропускаємо результати, які відповідають конфігураційним правилам
            yield item

    def run_pipeline(self) -> ProcessingStatistics:
        """Повний цикл виконання пайплайну з експортом результатів та звіту помилок."""
        # 1. Потокова фільтрація та експорт результатів у JSON
        valid_stream = self.stream_valid_results()
        filtered_stream = self.filter_results(valid_stream)

        exported_count = self._json_exporter.export(
            filtered_stream,
            self.config.output_path,
        )
        self.statistics.exported_records = exported_count

        # 2. Якщо є відхилені записи, експортуємо окремий звіт про помилки (JSON + CSV)
        if self.invalid_records:
            export_error_report_json(self.invalid_records, self.config.error_report_path)
            csv_err_path = self.config.error_report_path.with_suffix(".csv")
            self._csv_error_exporter.export_errors(self.invalid_records, csv_err_path)
            logger.info("Звіт про некоректні записи експортовано у %s та %s", self.config.error_report_path, csv_err_path)

        return self.statistics
