"""Модульні тести для атомарного експорту файлів (Task 29, 30, 73, 74, 99, 100)."""

import json
from pathlib import Path
import pytest

from sports_accounting.exceptions import DataExportError
from sports_accounting.exporters import JsonResultExporter, atomic_file_writer
from sports_accounting.models import Result


class TestExporters:
    """Тести атомарного запису та збереження цілісності файлів."""

    def test_atomic_file_writer_success(self, tmp_path: Path) -> None:
        target = tmp_path / "valid_output.txt"
        with atomic_file_writer(target) as f:
            f.write("Спортивні рекорди України")

        assert target.exists()
        assert target.read_text(encoding="utf-8") == "Спортивні рекорди України"
        # Перевірка очищення тимчасового файлу
        temp_file = target.with_suffix(target.suffix + ".tmp")
        assert not temp_file.exists()

    def test_atomic_file_writer_failure_preserves_old_data(self, tmp_path: Path) -> None:
        target = tmp_path / "existing_production.txt"
        target.write_text("Попередні валідні дані", encoding="utf-8")
        temp_file = target.with_suffix(target.suffix + ".tmp")

        # Симуляція раптового збою посеред запису
        with pytest.raises(DataExportError, match="Аварійний збій атомарного запису"):
            with atomic_file_writer(target) as f:
                f.write("Нові зламані дані...")
                raise RuntimeError("Імітація збою живлення або відсутності пам'яті")

        # Assert: цільовий файл НЕ пошкоджено, а тимчасовий видалено
        assert target.read_text(encoding="utf-8") == "Попередні валідні дані"
        assert not temp_file.exists()

    def test_json_result_exporter_success(
        self,
        tmp_path: Path,
        sample_results_list: list[Result],
    ) -> None:
        target_json = tmp_path / "exported_results.json"
        exporter = JsonResultExporter()

        count = exporter.export(sample_results_list, target_json)
        assert count == len(sample_results_list)
        assert target_json.exists()

        loaded_data = json.loads(target_json.read_text(encoding="utf-8"))
        assert len(loaded_data) == 4
        assert loaded_data[0]["athlete"]["name"] == "Ярослава Магучіх"
        assert loaded_data[0]["score"]["value"] == 2.10

    def test_json_result_exporter_handles_os_error(
        self,
        sample_results_list: list[Result],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        exporter = JsonResultExporter()
        invalid_path = Path("Z:/impossible_path/output.json")
        with pytest.raises(DataExportError):
            exporter.export(sample_results_list, invalid_path)
