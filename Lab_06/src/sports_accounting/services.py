"""Сервіс бізнес-логіки та координації обліку результатів."""

from pathlib import Path
from typing import Any

from sports_accounting.config import AppConfig
from sports_accounting.exceptions import (
    ExternalServiceError,
    RecordValidationError,
)
from sports_accounting.exporters import JsonResultExporter
from sports_accounting.models import RankingTable, Result
from sports_accounting.protocols import (
    AsyncExternalResultsProvider,
    Notifier,
    ResultExporter,
    ResultRepository,
)
from sports_accounting.readers import CsvResultsReader
from sports_accounting.validators import parse_and_validate_record


class SportsAccountingService:
    """Сервіс обліку спортивних результатів (Варіант 9)."""

    def __init__(
        self,
        repository: ResultRepository,
        notifier: Notifier,
        config: AppConfig,
        external_provider: AsyncExternalResultsProvider | None = None,
        exporter: ResultExporter | None = None,
    ) -> None:
        self._repository = repository
        self._notifier = notifier
        self._config = config
        self._external_provider = external_provider
        self._exporter = exporter or JsonResultExporter()
        self._reader = CsvResultsReader()

    def register_result(self, result: Result) -> None:
        """Реєструє результат у системі та надсилає сповіщення."""
        self._repository.add(result)
        message = (
            f"Новий результат: {result.athlete.name} — {result.score} "
            f"({result.sport.name}, {result.category})"
        )
        self._notifier.send("admin@sports.ua", message)

    def get_results_by_sport(self, sport_name: str) -> list[Result]:
        """Повертає список результатів за дисципліною."""
        return self._repository.find_by_sport(sport_name)

    def calculate_average_score(self, sport_name: str) -> float:
        """Обчислює середнє значення результату для дисципліни."""
        results = self.get_results_by_sport(sport_name)
        if not results:
            return 0.0
        total = sum(r.score.value for r in results)
        return round(total / len(results), 4)

    def find_best_result(self, sport_name: str) -> Result | None:
        """Знаходить рекордний (найкращий) результат у дисципліні."""
        results = self.get_results_by_sport(sport_name)
        if not results:
            return None

        is_lower_better = results[0].sport.is_lower_better
        if is_lower_better:
            return min(results, key=lambda r: r.score.value)
        return max(results, key=lambda r: r.score.value)

    def build_ranking_table(self, sport_name: str) -> RankingTable:
        """Формує турнірну таблицю для зазначеного виду спорту."""
        results = self.get_results_by_sport(sport_name)
        if not results:
            # Створюємо фіктивний об'єкт виду спорту для порожньої таблиці
            from sports_accounting.models import Sport
            dummy_sport = Sport(id=1, name=sport_name, unit="pts")
            return RankingTable(sport=dummy_sport, results=[])
        return RankingTable(sport=results[0].sport, results=results)

    def import_from_csv(
        self,
        path: Path,
        *,
        skip_invalid: bool = True,
    ) -> tuple[int, int]:
        """Потоковий імпорт із CSV з підтримкою strict/tolerant режимів."""
        valid_count = 0
        invalid_count = 0

        for line_number, raw_row in self._reader.read(path):
            try:
                result = parse_and_validate_record(
                    raw_row,
                    line_number=line_number,
                    config=self._config,
                )
                self.register_result(result)
                valid_count += 1
            except RecordValidationError:
                invalid_count += 1
                if skip_invalid:
                    continue
                raise

        return valid_count, invalid_count

    def export_to_json(self, sport_name: str, target_path: Path) -> int:
        """Експортує результати обраного виду спорту у файл JSON."""
        results = self.get_results_by_sport(sport_name)
        return self._exporter.export(results, target_path)

    async def sync_external_results(self, sport_name: str) -> int:
        """Асинхронно отримує та реєструє результати із зовнішнього провайдера."""
        if self._external_provider is None:
            raise ExternalServiceError("Зовнішній асинхронний провайдер результатів не налаштовано")

        try:
            remote_records = await self._external_provider.fetch_remote_results(sport_name)
        except Exception as error:
            raise ExternalServiceError(
                f"Не вдалося отримати віддалені дані для '{sport_name}': {error}"
            ) from error

        synced_count = 0
        for i, row in enumerate(remote_records, start=1):
            try:
                res = parse_and_validate_record(row, line_number=i, config=self._config)
                self.register_result(res)
                synced_count += 1
            except RecordValidationError:
                continue

        return synced_count
