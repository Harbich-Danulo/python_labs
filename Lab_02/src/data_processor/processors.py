"""Data processing functions: filtering, indexing, grouping, counting."""

from collections import Counter, defaultdict
from typing import Any, Callable


def get_unique_sports(records: list[dict[str, Any]]) -> set[str]:
    """Extract a set of unique sports using set comprehension."""
    return {item["sport"] for item in records}


def get_unique_categories(records: list[dict[str, Any]]) -> set[str]:
    """Extract a set of unique categories using set comprehension."""
    return {item["category"] for item in records}


def create_id_index(records: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Build a fast hash index (dict) by record ID using dict comprehension."""
    return {item["id"]: item for item in records}


def filter_by_sport(records: list[dict[str, Any]], sport: str) -> list[dict[str, Any]]:
    """Filter records by sport discipline using list comprehension."""
    target = sport.strip().lower()
    return [item for item in records if item["sport"].lower() == target]


def group_by_sport(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group athletes by sport discipline using defaultdict(list)."""
    groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in records:
        groups[item["sport"]].append(item)
    return dict(groups)


def group_by_category(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group athletes by competition category using defaultdict(list)."""
    groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in records:
        groups[item["category"]].append(item)
    return dict(groups)


def count_by_sport(records: list[dict[str, Any]]) -> Counter:
    """Count number of athletes per sport using collections.Counter."""
    return Counter(item["sport"] for item in records)


def count_by_category(records: list[dict[str, Any]]) -> Counter:
    """Count number of athletes per category using collections.Counter."""
    return Counter(item["category"] for item in records)


def nested_grouping(records: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Perform nested grouping (sport -> category -> list) using defaultdict."""
    nested: defaultdict[str, defaultdict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for item in records:
        nested[item["sport"]][item["category"]].append(item)
    return {k: dict(v) for k, v in nested.items()}


def universal_filter(
    items: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
) -> list[dict[str, Any]]:
    """Higher-order function for universal filtering by arbitrary predicate."""
    return [item for item in items if predicate(item)]
