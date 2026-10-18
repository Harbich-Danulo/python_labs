"""Domain models: Athlete, Sport, Competition, Result, RankingTable, RankingStrategy."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterator

from sports_app.value_objects import Score


class AthleteCategory(str, Enum):
    """Enumeration of standard competition categories."""
    JUNIORS = "Юніори"
    SENIORS = "Дорослі"
    MASTERS = "Майстри"


# 1. Domain Class: Athlete
@dataclass
class Athlete:
    """Domain Entity representing an athlete."""
    id: int
    name: str
    country: str = "Україна"
    age: int = 20

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Athlete name cannot be empty.")
        if self.age < 0:
            raise ValueError(f"Athlete age cannot be negative: {self.age}")

    def __str__(self) -> str:
        return f"{self.name} ({self.country}, {self.age} років)"


# 2. Domain Class: Sport
@dataclass
class Sport:
    """Domain Entity representing a sports discipline."""
    id: int
    name: str
    higher_is_better: bool = True
    default_unit: str = "pts"

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Sport name cannot be empty.")

    def __str__(self) -> str:
        direction = "більше=краще" if self.higher_is_better else "менше=краще"
        return f"{self.name} [{self.default_unit}, {direction}]"


# 3. Domain Class: Competition
@dataclass
class Competition:
    """Domain Entity representing a sports tournament."""
    id: int
    name: str
    location: str
    year: int = 2024

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Competition name cannot be empty.")
        if self.year < 1900:
            raise ValueError(f"Invalid competition year: {self.year}")

    def __str__(self) -> str:
        return f"{self.name} ({self.location}, {self.year})"


# 4. Domain Class: Result
@dataclass
class Result:
    """Domain Entity representing a competitive performance result.

    Implements composition (contains Athlete, Sport, Competition, Score) and property encapsulation.
    """
    id: int
    athlete: Athlete
    sport: Sport
    competition: Competition
    _score: Score
    category: AthleteCategory
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def score(self) -> Score:
        """Controlled property access to the encapsulated score value object."""
        return self._score

    @score.setter
    def score(self, new_score: Score) -> None:
        if new_score.value < 0:
            raise ValueError("Result score cannot be negative.")
        self._score = new_score

    def __str__(self) -> str:
        return (
            f"Result #{self.id}: {self.athlete.name} | {self.sport.name} | "
            f"{self.score} | {self.category.value} | {self.competition.name}"
        )


# 5. Abstract Base Class (ABC) for RankingStrategy (Strategy Pattern + OCP)
class RankingStrategy(ABC):
    """Abstract Base Class defining the strategy contract for ranking athletes."""

    @abstractmethod
    def sort_results(self, results: list[Result]) -> list[Result]:
        """Sort results according to the concrete strategy logic."""
        ...


# Concrete Subclasses of RankingStrategy (Inheritance & Polymorphism)
class HigherScoreWinsStrategy(RankingStrategy):
    """Ranking strategy where higher values win (high jump, gymnastics, points)."""

    def sort_results(self, results: list[Result]) -> list[Result]:
        return sorted(results, key=lambda r: r.score.value, reverse=True)


class LowerTimeWinsStrategy(RankingStrategy):
    """Ranking strategy where lower values win (races, swimming, track times)."""

    def sort_results(self, results: list[Result]) -> list[Result]:
        return sorted(results, key=lambda r: r.score.value, reverse=False)


# 6. Domain Class: RankingTable (Custom Collection Container with Dunder Methods)
@dataclass
class RankingTable:
    """Container managing competitive results with custom dunder methods (__len__, __iter__, __contains__, __getitem__)."""

    title: str
    strategy: RankingStrategy = field(default_factory=HigherScoreWinsStrategy)
    _results: list[Result] = field(default_factory=list)

    def add(self, result: Result) -> None:
        """Add a result to the ranking table."""
        self._results.append(result)

    def get_ranked(self) -> list[Result]:
        """Return results ordered according to the configured ranking strategy."""
        return self.strategy.sort_results(self._results)

    def __len__(self) -> int:
        return len(self._results)

    def __iter__(self) -> Iterator[Result]:
        return iter(self.get_ranked())

    def __contains__(self, result_id: int) -> bool:
        return any(r.id == result_id for r in self._results)

    def __getitem__(self, index: int) -> Result:
        ranked = self.get_ranked()
        return ranked[index]
