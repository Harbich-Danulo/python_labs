"""Analytics module: statistics, sorting, closures, *args, **kwargs, pipeline."""

from typing import Any, Callable

from data_processor.decorators import measure_time


@measure_time
def calculate_average(records: list[dict[str, Any]]) -> float:
    """Calculate average performance result using generator expression."""
    if not records:
        return 0.0
    # Generator expression inside sum() does not allocate an intermediate list
    total = sum(item["result"] for item in records)
    return round(total / len(records), 2)


def find_best_athlete(records: list[dict[str, Any]], key: str = "result") -> dict[str, Any] | None:
    """Find athlete with the highest score using lambda."""
    if not records:
        return None
    return max(records, key=lambda item: item[key])


def sort_by_result(records: list[dict[str, Any]], reverse: bool = True) -> list[dict[str, Any]]:
    """Sort athletes by result using lambda."""
    return sorted(records, key=lambda item: item["result"], reverse=reverse)


def universal_sort(
    records: list[dict[str, Any]],
    key_func: Callable[[dict[str, Any]], Any],
    reverse: bool = False,
) -> list[dict[str, Any]]:
    """Universal sorting higher-order function."""
    return sorted(records, key=key_func, reverse=reverse)


def calculate_average_values(*values: float) -> float:
    """Calculate average using *args for variable positional arguments."""
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def create_record(**fields: Any) -> dict[str, Any]:
    """Create a new athlete record using **kwargs for arbitrary keyword arguments."""
    return dict(fields)


def create_result_filter(min_result: float) -> Callable[[dict[str, Any]], bool]:
    """Closure factory: returns a predicate retaining min_result in its enclosing scope."""
    def predicate(athlete: dict[str, Any]) -> bool:
        return athlete["result"] >= min_result
    return predicate


def create_category_filter(category: str) -> Callable[[dict[str, Any]], bool]:
    """Closure factory: returns a predicate retaining category in its enclosing scope."""
    target = category.strip().lower()

    def predicate(athlete: dict[str, Any]) -> bool:
        return athlete["category"].strip().lower() == target
    return predicate


def pipeline_processing(
    data: list[dict[str, Any]],
    *stages: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Pipeline processing function that chains transformations using *args."""
    current = data
    for stage in stages:
        current = stage(current)
    return current
