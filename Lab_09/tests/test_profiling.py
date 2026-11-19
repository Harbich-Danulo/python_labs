"""Тестування інструментів профілювання (cProfile, tracemalloc) та головного модуля."""

from unittest.mock import patch
from sports_opt.analytics import statistics_python
from sports_opt.main import main
from sports_opt.profiling import profile_execution_cprofile, profile_memory_tracemalloc


def test_profile_execution_cprofile() -> None:
    data = [10.0, 11.0, 12.0]
    out = profile_execution_cprofile(statistics_python, data, top_n=5)
    assert "function calls" in out
    assert "ncalls" in out
    assert "cumtime" in out


def test_profile_memory_tracemalloc() -> None:
    data = [10.0] * 500
    curr_mb, peak_mb, stats = profile_memory_tracemalloc(statistics_python, data, top_n=3)
    assert peak_mb >= 0.0
    assert isinstance(stats, list)


def test_main_execution() -> None:
    with patch("builtins.print") as mock_print:
        main()
        assert mock_print.called
