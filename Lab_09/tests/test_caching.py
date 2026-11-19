"""Тестування модуля кешування та механізму інвалідації кешу."""

from typing import List
import pytest
from sports_opt.caching import SportsRatingService, get_cache_metrics
from sports_opt.models import SportResult


def test_caching_and_invalidation(sample_sports_data: List[SportResult]) -> None:
    service = SportsRatingService(sample_sports_data[:50])
    service.clear_cache()

    # 1. Холодний виклик (miss)
    stats1 = service.calculate_stats_cached(sport_id=1)
    metrics_after_cold = get_cache_metrics()
    assert metrics_after_cold["misses"] >= 1

    # 2. Гарячий виклик (hit)
    stats2 = service.calculate_stats_cached(sport_id=1)
    assert stats2 == stats1
    metrics_after_warm = get_cache_metrics()
    assert metrics_after_warm["hits"] >= 1

    # 3. Інвалідація через додавання нового рекорду
    new_record = SportResult(
        id=88888,
        athlete_id=1,
        athlete_name="Атлет",
        sport_id=1,
        sport_name="Біг на 100м",
        score=999.0,
        category="Дорослі",
    )
    service.add_result(new_record)
    assert service.version == 2

    # 4. Виклик після інвалідації повинен повернути нове значення
    stats3 = service.calculate_stats_cached(sport_id=1)
    assert stats3 != stats1
    assert stats3[2] == pytest.approx(999.0)  # max_score оновився до 999.0


def test_uncached_vs_cached(sample_sports_data: List[SportResult]) -> None:
    service = SportsRatingService(sample_sports_data[:30])
    uncached = service.calculate_stats_uncached(sport_id=1)
    cached = service.calculate_stats_cached(sport_id=1)

    assert cached[0] == pytest.approx(uncached["average"])
    assert cached[1] == pytest.approx(uncached["minimum"])
    assert cached[2] == pytest.approx(uncached["maximum"])
    assert cached[3] == pytest.approx(uncached["std"])
