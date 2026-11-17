"""Тестування модуля main.py та консольного інтерфейсу."""

from unittest.mock import patch
import pytest

from sports_accounting.main import ConsoleNotifier, main


def test_console_notifier_send(capsys: pytest.CaptureFixture[str]) -> None:
    notifier = ConsoleNotifier()
    notifier.send("user@test.com", "Тестове повідомлення")
    captured = capsys.readouterr()
    assert "[NOTIFICATION to user@test.com]: Тестове повідомлення" in captured.out


def test_main_execution_with_config(capsys: pytest.CaptureFixture[str]) -> None:
    # Запуск main() при наявному config.yaml
    main()
    captured = capsys.readouterr()
    assert "=== СИСТЕМА ОБЛІКУ СПОРТИВНИХ РЕЗУЛЬТАТІВ ===" in captured.out


def test_main_execution_missing_config(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Симуляція відсутності config.yaml
    with patch("sports_accounting.main.Path.exists", return_value=False):
        main()
    captured = capsys.readouterr()
    assert "відсутній" in captured.out
