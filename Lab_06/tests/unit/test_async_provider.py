"""Тестування асинхронних залежностей за допомогою AsyncMock (Варіант 9, Task 44, 45, 77, 78)."""

from unittest.mock import AsyncMock, Mock
import pytest

from sports_accounting.config import AppConfig
from sports_accounting.exceptions import ExternalServiceError
from sports_accounting.protocols import AsyncExternalResultsProvider, Notifier
from sports_accounting.repositories import InMemoryResultRepository
from sports_accounting.services import SportsAccountingService


class TestAsyncExternalResultsProvider:
    """Тестування асинхронної взаємодії із зовнішнім провайдером результатів."""

    @pytest.mark.asyncio
    async def test_sync_external_results_success(self, sample_config: AppConfig) -> None:
        # Arrange
        mock_provider = Mock(spec=AsyncExternalResultsProvider)
        mock_provider.fetch_remote_results = AsyncMock(
            return_value=[
                {
                    "id": 100,
                    "athlete_id": 501,
                    "athlete": "Богдан Бондаренко",
                    "age": 34,
                    "country": "Україна",
                    "sport_id": 1,
                    "sport": "Стрибки у висоту",
                    "unit": "m",
                    "is_lower_better": "false",
                    "competition_id": 1,
                    "competition": "Diamond League",
                    "location": "Цюрих",
                    "year": 2024,
                    "result": 2.22,
                    "category": "Дорослі",
                    "timestamp": "2024-08-01T19:00:00",
                }
            ]
        )

        mock_notifier = Mock(spec=Notifier)
        repo = InMemoryResultRepository()
        service = SportsAccountingService(
            repository=repo,
            notifier=mock_notifier,
            config=sample_config,
            external_provider=mock_provider,
        )

        # Act
        synced_count = await service.sync_external_results("Стрибки у висоту")

        # Assert
        assert synced_count == 1
        assert repo.count() == 1
        saved = repo.get(100)
        assert saved is not None
        assert saved.athlete.name == "Богдан Бондаренко"

        # Перевірка виклику асинхронного методу (Task 62)
        mock_provider.fetch_remote_results.assert_awaited_once_with("Стрибки у висоту")
        mock_notifier.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_external_results_failure_raises(self, sample_config: AppConfig) -> None:
        # Arrange
        mock_provider = Mock(spec=AsyncExternalResultsProvider)
        mock_provider.fetch_remote_results = AsyncMock(
            side_effect=ConnectionError("Віддалений сервер API недоступний")
        )

        mock_notifier = Mock(spec=Notifier)
        repo = InMemoryResultRepository()
        service = SportsAccountingService(
            repository=repo,
            notifier=mock_notifier,
            config=sample_config,
            external_provider=mock_provider,
        )

        # Act & Assert
        with pytest.raises(ExternalServiceError, match="Не вдалося отримати віддалені дані") as exc_info:
            await service.sync_external_results("Стрибки у висоту")

        # Перевірка Exception Chaining у асинхронному сценарії
        assert isinstance(exc_info.value.__cause__, ConnectionError)
        mock_notifier.send.assert_not_called()
        assert repo.count() == 0

    @pytest.mark.asyncio
    async def test_sync_without_configured_provider_raises(self, sample_config: AppConfig) -> None:
        mock_notifier = Mock(spec=Notifier)
        repo = InMemoryResultRepository()
        service = SportsAccountingService(
            repository=repo,
            notifier=mock_notifier,
            config=sample_config,
            external_provider=None,  # No provider!
        )

        with pytest.raises(ExternalServiceError, match="не налаштовано"):
            await service.sync_external_results("Стрибки у висоту")
