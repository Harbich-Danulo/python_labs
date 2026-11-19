"""Тестування правильності роботи аналітичних алгоритмів (Python vs NumPy)."""

from typing import List
import numpy as np
import pytest
from sports_opt.analytics import (
    category_statistics_numpy,
    category_statistics_python,
    ranking_numpy,
    ranking_python,
    score_complex_transform,
    statistics_numpy,
    statistics_python,
)
from sports_opt.models import SportResult


def test_statistics_python_vs_numpy(sample_scores: List[float]) -> None:
    py_res = statistics_python(sample_scores)
    np_res = statistics_numpy(sample_scores)

    assert np_res["average"] == pytest.approx(py_res["average"], rel=1e-5)
    assert np_res["minimum"] == pytest.approx(py_res["minimum"], rel=1e-5)
    assert np_res["maximum"] == pytest.approx(py_res["maximum"], rel=1e-5)
    assert np_res["std"] == pytest.approx(py_res["std"], rel=1e-5)


def test_statistics_empty_list() -> None:
    res = statistics_python([])
    assert res["average"] == 0.0
    res_np = statistics_numpy([])
    assert res_np["average"] == 0.0


def test_score_complex_transform() -> None:
    val = score_complex_transform(10.5)
    assert isinstance(val, float)
    assert val > 0.0


def test_ranking_python_and_numpy(sample_sports_data: List[SportResult]) -> None:
    subset = sample_sports_data[:50]
    rank_py = ranking_python(subset, is_lower_better=True)
    assert len(rank_py) == 50
    assert rank_py[0]["rank"] == 1
    assert rank_py[0]["score"] <= rank_py[1]["score"]

    scores_arr = np.array([r.score for r in subset])
    indices = ranking_numpy(scores_arr, is_lower_better=True)
    sorted_scores_np = scores_arr[indices]
    assert sorted_scores_np[0] <= sorted_scores_np[1]


def test_category_statistics(sample_sports_data: List[SportResult]) -> None:
    subset = sample_sports_data[:100]
    py_cat = category_statistics_python(subset)
    np_cat = category_statistics_numpy(subset)

    assert set(py_cat.keys()) == set(np_cat.keys())
    for cat in py_cat:
        assert np_cat[cat]["average"] == pytest.approx(py_cat[cat]["average"], rel=1e-5)
        assert np_cat[cat]["std"] == pytest.approx(py_cat[cat]["std"], rel=1e-5)
