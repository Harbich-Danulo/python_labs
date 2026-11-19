"""Модуль кешування (Caching), LRU-кешу та механізму інвалідації кешу (Cache Invalidation)."""

from __future__ import annotations
from functools import lru_cache
from typing import Any, Dict, List, Tuple
from sports_opt.analytics import statistics_python
from sports_opt.models import SportResult


class SportsRatingService:
    """Сервіс рейтингу із вбудованим LRU-кешуванням та автоматичною інвалідацією при змінах."""

    def __init__(self, initial_data: List[SportResult] | None = None) -> None:
        self.data: List[SportResult] = list(initial_data) if initial_data else []
        self.version: int = 1

    def add_result(self, result: SportResult) -> None:
        """Додає новий результат та інвалідує кеш шляхом зміни версії даних."""
        self.data.append(result)
        self.version += 1

    def get_sport_scores(self, sport_id: int) -> List[float]:
        """Отримує бали конкретного виду спорту."""
        return [r.score for r in self.data if r.sport_id == sport_id]

    def get_category_scores(self, category: str) -> List[float]:
        """Отримує бали конкретної вікової категорії."""
        return [r.score for r in self.data if r.category == category]

    def calculate_stats_uncached(self, sport_id: int) -> Dict[str, float]:
        """Обчислення статистики без використання кешу."""
        scores = self.get_sport_scores(sport_id)
        return statistics_python(scores)

    def calculate_stats_cached(self, sport_id: int) -> Tuple[float, float, float, float]:
        """Обчислення статистики через функцію з lru_cache з прив'язкою до поточної версії."""
        return _cached_sport_statistics(self, sport_id, self.version)

    def clear_cache(self) -> None:
        """Примусове скидання внутрішнього кешу."""
        _cached_sport_statistics.cache_clear()


@lru_cache(maxsize=128)
def _cached_sport_statistics(
    service: SportsRatingService, sport_id: int, version: int
) -> Tuple[float, float, float, float]:
    """Дорога операція розрахунку статистики: результат кешується доки (sport_id, version) незмінні."""
    scores = service.get_sport_scores(sport_id)
    stats = statistics_python(scores)
    return (stats["average"], stats["minimum"], stats["maximum"], stats["std"])


def get_cache_metrics() -> Dict[str, Any]:
    """Повертає статистику роботи кешу (hits, misses, currsize, maxsize)."""
    info = _cached_sport_statistics.cache_info()
    return {
        "hits": info.hits,
        "misses": info.misses,
        "currsize": info.currsize,
        "maxsize": info.maxsize,
    }
