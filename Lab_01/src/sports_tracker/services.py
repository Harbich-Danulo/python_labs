"""Business logic services for sports results management."""

from sports_tracker.models import Athlete

DEFAULT_PRECISION: int = 2


def add_result(athletes: list[Athlete], athlete: Athlete) -> None:
    """Add a new athlete result to the collection.

    Args:
        athletes: Target list of athletes.
        athlete: Athlete instance to append.
    """
    athletes.append(athlete)


def filter_by_sport(athletes: list[Athlete], sport: str) -> list[Athlete]:
    """Find all athletes participating in a given sport.

    Args:
        athletes: List of athletes to filter.
        sport: Name of the sport (case-insensitive).

    Returns:
        Filtered list of athletes.
    """
    target = sport.strip().lower()
    return [
        athlete
        for athlete in athletes
        if athlete.sport.lower() == target
    ]


def filter_by_multiple_criteria(
    athletes: list[Athlete],
    sport: str | None = None,
    category: str | None = None,
) -> list[Athlete]:
    """Filter athletes by sport and/or category.

    Args:
        athletes: Source list of athletes.
        sport: Optional sport name to filter by.
        category: Optional category name to filter by.

    Returns:
        List of matching athletes.
    """
    result = athletes
    if sport is not None and sport.strip():
        target_sport = sport.strip().lower()
        result = [a for a in result if a.sport.lower() == target_sport]
    if category is not None and category.strip():
        target_category = category.strip().lower()
        result = [a for a in result if a.category.lower() == target_category]
    return result


def find_best_result(
    athletes: list[Athlete],
    sport: str | None = None,
    higher_is_better: bool = True,
) -> Athlete | None:
    """Determine the athlete with the best result.

    Args:
        athletes: List of athletes.
        sport: Optional sport to restrict the search to.
        higher_is_better: True if higher value wins (e.g. points, jump height),
                          False if lower is better (e.g. race time).

    Returns:
        Athlete with the best result, or None if list is empty.
    """
    candidates = filter_by_sport(athletes, sport) if sport else athletes
    if not candidates:
        return None

    if higher_is_better:
        return max(candidates, key=lambda a: a.result)
    return min(candidates, key=lambda a: a.result)


def calculate_average_result(
    athletes: list[Athlete],
    sport: str | None = None,
) -> float:
    """Calculate the average performance result.

    Args:
        athletes: List of athletes.
        sport: Optional sport to restrict the calculation to.

    Returns:
        Average numeric result rounded to DEFAULT_PRECISION, or 0.0 if empty.
    """
    candidates = filter_by_sport(athletes, sport) if sport else athletes
    if not candidates:
        return 0.0

    total = sum(a.result for a in candidates)
    avg = total / len(candidates)
    return round(avg, DEFAULT_PRECISION)


def generate_ranking(
    athletes: list[Athlete],
    sport: str | None = None,
    descending: bool = True,
) -> list[Athlete]:
    """Generate a sorted ranking of athletes by their performance result.

    Args:
        athletes: List of athletes.
        sport: Optional sport to filter before ranking.
        descending: True for descending order (highest first),
                    False for ascending (lowest first).

    Returns:
        Sorted list of athletes.
    """
    candidates = filter_by_sport(athletes, sport) if sport else athletes
    return sorted(candidates, key=lambda a: a.result, reverse=descending)


def calculate_statistics(
    athletes: list[Athlete],
    sport: str | None = None,
) -> dict[str, float | int]:
    """Compute summary statistics for athletes.

    Args:
        athletes: List of athletes.
        sport: Optional sport to compute stats for.

    Returns:
        Dictionary with count, average, min_result, max_result.
    """
    candidates = filter_by_sport(athletes, sport) if sport else athletes
    if not candidates:
        return {"count": 0, "average": 0.0, "min_result": 0.0, "max_result": 0.0}

    results = [a.result for a in candidates]
    return {
        "count": len(candidates),
        "average": round(sum(results) / len(results), DEFAULT_PRECISION),
        "min_result": min(results),
        "max_result": max(results),
    }
