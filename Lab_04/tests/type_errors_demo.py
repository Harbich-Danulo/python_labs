"""Demonstration of 3 intentional type errors for Section 71 of Laboratory Work 4."""

from sports_app.models import Athlete
from sports_app.repositories import InMemoryRepository
from sports_app.value_objects import Score


def demo_type_errors() -> None:
    # Error 1: Incompatible types in assignment (expression has type "str", variable has type "int")
    athlete_id: int = "101"

    # Error 2: Incompatible return value type (got "str", expected "int")
    def get_rank() -> int:
        return "1st"

    # Error 3: Argument 1 to "add" of "InMemoryRepository" has incompatible type "Score"; expected "Athlete"
    repo: InMemoryRepository[Athlete] = InMemoryRepository[Athlete]()
    score: Score = Score(2.10, "m")
    repo.add(score)
