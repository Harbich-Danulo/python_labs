"""Аналітичні обчислення: генерація наборів даних, базові Python-алгоритми та векторизація NumPy."""

from __future__ import annotations
import math
import random
from typing import Any, Dict, List
import numpy as np
from sports_opt.models import SportResult

CATEGORIES: list[str] = ["Юніори", "Молодь", "Дорослі", "Майстри"]
SPORTS: list[tuple[int, str, str, bool]] = [
    (1, "Біг на 100м", "сек", True),
    (2, "Плавання 50м", "сек", True),
    (3, "Стрибки у довжину", "м", False),
    (4, "Метання списа", "м", False),
]
ATHLETES: list[str] = [
    "Данило Гарбіч", "Олександр Зінченко", "Михайло Мудрик", "Ярослава Магучіх",
    "Михайло Романчук", "Ольга Харлан", "Жан Беленюк", "Еліна Світоліна",
    "Андрій Шевченко", "Сергій Бубка"
]


def generate_sports_dataset(count: int, seed: int = 42) -> List[SportResult]:
    """Генерує великий синтетичний набір спортивних результатів для профілювання."""
    rng = random.Random(seed)
    results: List[SportResult] = []

    for i in range(1, count + 1):
        sport_info = rng.choice(SPORTS)
        athlete_name = rng.choice(ATHLETES)
        athlete_id = (i % 500) + 1
        category = rng.choice(CATEGORIES)

        # Базовий результат залежно від дисципліни
        if sport_info[0] == 1:  # Біг 100м
            score = round(rng.uniform(9.8, 14.5), 2)
        elif sport_info[0] == 2:  # Плавання 50м
            score = round(rng.uniform(21.0, 32.0), 2)
        elif sport_info[0] == 3:  # Стрибки
            score = round(rng.uniform(5.5, 8.9), 2)
        else:  # Метання
            score = round(rng.uniform(60.0, 95.0), 2)

        results.append(
            SportResult(
                id=i,
                athlete_id=athlete_id,
                athlete_name=athlete_name,
                sport_id=sport_info[0],
                sport_name=sport_info[1],
                score=score,
                category=category,
                competition_name=f"Турнір #{rng.randint(1, 20)}",
            )
        )
    return results


def score_complex_transform(score: float) -> float:
    """Важка CPU-bound математична функція (симуляція біометричного рейтингового коефіцієнта)."""
    val = score
    for _ in range(60):
        val = (
            math.sin(val) ** 2
            + math.cos(val) ** 2
            + math.sqrt(abs(val) + 1.0)
        )
    return val


def calculate_scores_sequential(scores: List[float]) -> List[float]:
    """Послідовна обчислювальна обробка списку результатів (Baseline)."""
    return [score_complex_transform(s) for s in scores]


def statistics_python(values: List[float]) -> Dict[str, float]:
    """Обчислення статистичних показників чистими циклами Python (Baseline)."""
    n = len(values)
    if n == 0:
        return {"average": 0.0, "minimum": 0.0, "maximum": 0.0, "std": 0.0}

    total = 0.0
    min_val = values[0]
    max_val = values[0]

    for v in values:
        total += v
        if v < min_val:
            min_val = v
        if v > max_val:
            max_val = v

    avg_val = total / n

    variance_sum = 0.0
    for v in values:
        variance_sum += (v - avg_val) ** 2
    std_val = math.sqrt(variance_sum / n)

    return {
        "average": float(avg_val),
        "minimum": float(min_val),
        "maximum": float(max_val),
        "std": float(std_val),
    }


def statistics_numpy(values: List[float]) -> Dict[str, float]:
    """Векторизоване обчислення статистичних показників за допомогою бібліотеки NumPy."""
    if not values:
        return {"average": 0.0, "minimum": 0.0, "maximum": 0.0, "std": 0.0}

    arr = np.asarray(values, dtype=np.float64)
    return {
        "average": float(arr.mean()),
        "minimum": float(arr.min()),
        "maximum": float(arr.max()),
        "std": float(arr.std()),
    }


def ranking_python(results: List[SportResult], is_lower_better: bool = False) -> List[Dict[str, Any]]:
    """Формування рейтингу на основі стандартного сортування Python (Timsort)."""
    sorted_res = sorted(results, key=lambda r: r.score, reverse=not is_lower_better)
    ranking: List[Dict[str, Any]] = []
    for rank, item in enumerate(sorted_res, start=1):
        ranking.append({
            "rank": rank,
            "id": item.id,
            "athlete_name": item.athlete_name,
            "score": item.score,
            "category": item.category,
        })
    return ranking


def ranking_numpy(scores: np.ndarray[Any, Any], is_lower_better: bool = False) -> np.ndarray[Any, Any]:
    """Векторизоване сортування масиву балів через NumPy argsort."""
    indices = np.argsort(scores)
    if not is_lower_better:
        indices = indices[::-1]
    return indices


def category_statistics_python(results: List[SportResult]) -> Dict[str, Dict[str, float]]:
    """Групування та обчислення статистики за категоріями засобами Python."""
    cat_buckets: Dict[str, List[float]] = {}
    for r in results:
        if r.category not in cat_buckets:
            cat_buckets[r.category] = []
        cat_buckets[r.category].append(r.score)

    stats_by_cat: Dict[str, Dict[str, float]] = {}
    for cat, scores in cat_buckets.items():
        stats_by_cat[cat] = statistics_python(scores)
    return stats_by_cat


def category_statistics_numpy(results: List[SportResult]) -> Dict[str, Dict[str, float]]:
    """Групування та векторизована обробка статистики категорій через NumPy."""
    cat_buckets: Dict[str, List[float]] = {}
    for r in results:
        if r.category not in cat_buckets:
            cat_buckets[r.category] = []
        cat_buckets[r.category].append(r.score)

    stats_by_cat: Dict[str, Dict[str, float]] = {}
    for cat, scores in cat_buckets.items():
        stats_by_cat[cat] = statistics_numpy(scores)
    return stats_by_cat
