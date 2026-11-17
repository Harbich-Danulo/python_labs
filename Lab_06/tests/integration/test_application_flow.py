"""Наскрізний інтеграційний тест бізнес-сценарію системи (End-to-End application flow)."""

from datetime import datetime
import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock
import pytest

from sports_accounting.config import load_config
from sports_accounting.value_objects import Score
from sports_accounting.protocols import AsyncExternalResultsProvider, Notifier
from sports_accounting.repositories import InMemoryResultRepository
from sports_accounting.services import SportsAccountingService


@pytest.mark.integration
class TestApplicationFlowIntegration:
    """Наскрізні сценарії: Async API + CSV Import + Domain Service + Ranking + Export."""

    @pytest.mark.asyncio
    async def test_complete_competition_ranking_lifecycle(self, tmp_path: Path) -> None:
        # 1. Завантажуємо тестову конфігурацію
        cfg_file = tmp_path / "app_config.yaml"
        cfg_file.write_text(
            "input:\n"
            "  path: input_data.csv\n"
            "output:\n"
            f"  path: {tmp_path.as_posix()}/final_rankings.json\n"
            "env_mode: testing\n"
            "processing:\n"
            "  allowed_sports: ['Стрибки у висоту']\n"
            "  allowed_categories: ['Дорослі']\n"
            "  sport_rules:\n"
            "    'Стрибки у висоту':\n"
            "      min_value: 1.0\n"
            "      max_value: 2.5\n",
            encoding="utf-8",
        )
        config = load_config(cfg_file)

        # 2. Налаштування компонентів та подвійників тестування
        mock_notifier = Mock(spec=Notifier)
        mock_async_provider = Mock(spec=AsyncExternalResultsProvider)
        mock_async_provider.fetch_remote_results = AsyncMock(
            return_value=[
                {
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
                },
                {
                    "id": 2,
                    "athlete_id": 102,
                    "athlete": "Ірина Геращенко",
                    "age": 29,
                    "country": "Україна",
                    "sport_id": 1,
                    "sport": "Стрибки у висоту",
                    "unit": "m",
                    "is_lower_better": "false",
                    "competition_id": 1,
                    "competition": "Diamond League",
                    "location": "Париж",
                    "year": 2024,
                    "result": 2.00,
                    "category": "Дорослі",
                    "timestamp": "2024-07-07T18:30:00",
                },
            ]
        )

        repo = InMemoryResultRepository()
        service = SportsAccountingService(
            repository=repo,
            notifier=mock_notifier,
            config=config,
            external_provider=mock_async_provider,
        )

        # 3. Синхронізація віддалених результатів
        synced = await service.sync_external_results("Стрибки у висоту")
        assert synced == 2
        assert repo.count() == 2

        # 4. Додаткова реєстрація локального результату (створення нічиєї для 2-го місця)
        from sports_accounting.models import Athlete, Competition, Result, Sport
        tie_result = Result(
            id=3,
            athlete=Athlete(id=103, name="Юлія Левченко", age=26),
            sport=Sport(id=1, name="Стрибки у висоту", unit="m"),
            competition=Competition(id=1, name="Diamond League", location="Париж", year=2024),
            score=Score(2.00, "m"),
            category="Дорослі",
            timestamp=datetime(2024, 7, 7, 18, 30),
        )
        service.register_result(tie_result)
        assert repo.count() == 3

        # 5. Побудова турнірної таблиці та перевірка логіки розділеного рангу
        ranking_table = service.build_ranking_table("Стрибки у висоту")
        assert len(ranking_table) == 3
        # 1 місце: Магучіх (2.10)
        assert ranking_table[0].rank == 1
        assert ranking_table[0].result.athlete.name == "Ярослава Магучіх"
        # 2 місце: Геращенко (2.00) та Левченко (2.00) ділять 2-й ранг!
        assert ranking_table[1].rank == 2
        assert ranking_table[2].rank == 2

        # 6. Обчислення статистики
        avg_score = service.calculate_average_score("Стрибки у висоту")
        # (2.10 + 2.00 + 2.00) / 3 = 2.0333...
        assert avg_score == pytest.approx(2.0333, abs=1e-3)

        # 7. Експорт у JSON та перевірка файлового виводу
        export_file = tmp_path / "final_rankings.json"
        exported_cnt = service.export_to_json("Стрибки у висоту", export_file)
        assert exported_cnt == 3
        assert export_file.exists()

        content = json.loads(export_file.read_text(encoding="utf-8"))
        assert len(content) == 3
        assert content[0]["athlete"]["name"] == "Ярослава Магучіх"
