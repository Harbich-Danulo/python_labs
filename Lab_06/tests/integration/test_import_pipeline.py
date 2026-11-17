"""Інтеграційні тести файлового конвеєра: CSV -> Validation -> Service -> JSON Export."""

import json
from pathlib import Path
from unittest.mock import Mock
import pytest

from sports_accounting.config import AppConfig
from sports_accounting.exceptions import RecordValidationError
from sports_accounting.protocols import Notifier
from sports_accounting.repositories import InMemoryResultRepository
from sports_accounting.services import SportsAccountingService


@pytest.mark.integration
class TestImportExportPipelineIntegration:
    """Інтеграційне тестування конвеєра імпорту та експорту даних."""

    def test_full_pipeline_csv_to_json(self, tmp_path: Path, sample_config: AppConfig) -> None:
        # Arrange
        csv_file = tmp_path / "integration_input.csv"
        csv_file.write_text(
            "id,athlete_id,athlete,age,country,sport_id,sport,unit,is_lower_better,competition_id,competition,location,year,result,category,timestamp\n"
            "1,101,Ярослава Магучіх,22,Україна,1,Стрибки у висоту,m,false,1,Diamond League,Париж,2024,2.10,Дорослі,2024-07-07T18:30:00\n"
            "2,102,Ірина Геращенко,29,Україна,1,Стрибки у висоту,m,false,2,Олімпійські Ігри,Париж,2024,2.00,Дорослі,2024-08-04T19:00:00\n"
            "3,103,Невалідний Рядок,20,Україна,1,Стрибки у висоту,m,false,1,Турнір,Київ,2024,99.00,Дорослі,2024-07-10T12:00:00\n",
            encoding="utf-8",
        )
        json_output = tmp_path / "integration_output.json"

        mock_notifier = Mock(spec=Notifier)
        repo = InMemoryResultRepository()
        service = SportsAccountingService(
            repository=repo,
            notifier=mock_notifier,
            config=sample_config,
        )

        # Act: 1. Потоковий імпорт у tolerant режимі
        valid_cnt, invalid_cnt = service.import_from_csv(csv_file, skip_invalid=True)

        # Assert імпорту
        assert valid_cnt == 2
        assert invalid_cnt == 1
        assert repo.count() == 2
        assert mock_notifier.send.call_count == 2

        # Act: 2. Атомарний експорт результатів у JSON
        exported_cnt = service.export_to_json("Стрибки у висоту", json_output)

        # Assert експорту
        assert exported_cnt == 2
        assert json_output.exists()

        exported_data = json.loads(json_output.read_text(encoding="utf-8"))
        assert len(exported_data) == 2
        assert exported_data[0]["athlete"]["name"] == "Ярослава Магучіх"
        assert exported_data[1]["athlete"]["name"] == "Ірина Геращенко"

    def test_strict_mode_aborts_pipeline_without_corrupting_state(
        self,
        tmp_path: Path,
        sample_config: AppConfig,
    ) -> None:
        csv_file = tmp_path / "strict_fail.csv"
        csv_file.write_text(
            "id,athlete_id,athlete,age,country,sport_id,sport,unit,is_lower_better,competition_id,competition,location,year,result,category,timestamp\n"
            "1,101,Ярослава Магучіх,22,Україна,1,Стрибки у висоту,m,false,1,Diamond League,Париж,2024,2.10,Дорослі,2024-07-07T18:30:00\n"
            "2,102,,22,Україна,1,Стрибки у висоту,m,false,1,ЧУ,Львів,2024,2.00,Дорослі,2024-07-07T18:30:00\n",
            encoding="utf-8",
        )
        mock_notifier = Mock(spec=Notifier)
        repo = InMemoryResultRepository()
        service = SportsAccountingService(repo, mock_notifier, sample_config)

        with pytest.raises(RecordValidationError):
            service.import_from_csv(csv_file, skip_invalid=False)

        # Лише перший успішний запис потрапив у репозиторій до переривання
        assert repo.count() == 1
