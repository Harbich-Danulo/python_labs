"""Тестування завантаження та валідації конфігурації із застосуванням monkeypatch (Task 32-35, 72)."""

from pathlib import Path
import pytest

from sports_accounting.config import load_config
from sports_accounting.exceptions import ConfigurationError


class TestConfiguration:
    """Тести для модуля config.py з перевіркою змінних оточення."""

    @pytest.fixture
    def valid_yaml_file(self, tmp_path: Path) -> Path:
        cfg_file = tmp_path / "valid_config.yaml"
        cfg_file.write_text(
            "input:\n"
            "  path: data/sports.csv\n"
            "output:\n"
            "  path: output/sports.json\n"
            "env_mode: testing\n"
            "logging:\n"
            "  level: INFO\n"
            "processing:\n"
            "  allowed_sports: ['Стрибки у висоту']\n"
            "  allowed_categories: ['Дорослі']\n"
            "  sport_rules:\n"
            "    'Стрибки у висоту':\n"
            "      min_value: 1.0\n"
            "      max_value: 2.5\n",
            encoding="utf-8",
        )
        return cfg_file

    def test_load_valid_config(self, valid_yaml_file: Path) -> None:
        cfg = load_config(valid_yaml_file)
        assert cfg.env_mode == "testing"
        assert "Стрибки у висоту" in cfg.allowed_sports
        assert cfg.sport_rules["Стрибки у висоту"].min_value == 1.0

    def test_monkeypatch_environment_variable_override(
        self,
        valid_yaml_file: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Підміна змінної оточення APP_ENV через monkeypatch (Task 33)
        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.setenv("SPORTS_LOG_LEVEL", "DEBUG")

        cfg = load_config(valid_yaml_file)
        assert cfg.env_mode == "production"
        assert cfg.log_level == "DEBUG"

    def test_monkeypatch_delenv_reverts_to_default(
        self,
        valid_yaml_file: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("APP_ENV", raising=False)
        monkeypatch.delenv("SPORTS_LOG_LEVEL", raising=False)

        cfg = load_config(valid_yaml_file)
        assert cfg.env_mode == "testing"
        assert cfg.log_level == "INFO"

    def test_missing_config_file_raises(self, tmp_path: Path) -> None:
        missing = tmp_path / "non_existent.yaml"
        with pytest.raises(ConfigurationError, match="не знайдено"):
            load_config(missing)

    def test_invalid_yaml_syntax_raises(self, tmp_path: Path) -> None:
        bad_yaml = tmp_path / "bad_syntax.yaml"
        bad_yaml.write_text("input: [unclosed_list", encoding="utf-8")
        with pytest.raises(ConfigurationError, match="Синтаксична помилка у файлі YAML"):
            load_config(bad_yaml)

    def test_non_mapping_yaml_raises(self, tmp_path: Path) -> None:
        bad_yaml = tmp_path / "list_root.yaml"
        bad_yaml.write_text("- item1\n- item2", encoding="utf-8")
        with pytest.raises(ConfigurationError, match="має бути словником"):
            load_config(bad_yaml)

    def test_empty_allowed_sports_raises(self, tmp_path: Path) -> None:
        bad_yaml = tmp_path / "empty_sports.yaml"
        bad_yaml.write_text(
            "input: { path: in.csv }\noutput: { path: out.json }\n"
            "processing:\n  allowed_sports: []\n  allowed_categories: ['Дорослі']\n",
            encoding="utf-8",
        )
        with pytest.raises(ConfigurationError, match="allowed_sports"):
            load_config(bad_yaml)

    def test_invalid_sport_rule_range_raises(self, tmp_path: Path) -> None:
        bad_yaml = tmp_path / "bad_range.yaml"
        bad_yaml.write_text(
            "input: { path: in.csv }\noutput: { path: out.json }\n"
            "processing:\n"
            "  allowed_sports: ['Стрибки']\n"
            "  allowed_categories: ['Дорослі']\n"
            "  sport_rules:\n"
            "    'Стрибки': { min_value: 10.0, max_value: 2.0 }\n",
            encoding="utf-8",
        )
        with pytest.raises(ConfigurationError, match="min_value.*> max_value"):
            load_config(bad_yaml)
