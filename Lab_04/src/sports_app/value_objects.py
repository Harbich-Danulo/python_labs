"""Immutable value objects for sports results domain."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Score:
    """Immutable Value Object representing an athletic measurement (e.g. meters, points, seconds).

    Implements validation, dunder methods (__add__, __str__, __repr__), and arithmetic.
    """
    value: float
    unit: str = "pts"

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError(f"Score value cannot be negative: {self.value}")
        if not self.unit.strip():
            raise ValueError("Score unit cannot be empty.")

    def __add__(self, other: "Score") -> "Score":
        if not isinstance(other, Score):
            return NotImplemented
        if self.unit != other.unit:
            raise ValueError(f"Unit mismatch: cannot add {self.unit} and {other.unit}")
        return Score(round(self.value + other.value, 4), self.unit)

    def __sub__(self, other: "Score") -> "Score":
        if not isinstance(other, Score):
            return NotImplemented
        if self.unit != other.unit:
            raise ValueError(f"Unit mismatch: cannot subtract {self.unit} and {other.unit}")
        new_val = round(self.value - other.value, 4)
        if new_val < 0:
            raise ValueError(f"Subtraction resulted in negative score: {new_val}")
        return Score(new_val, self.unit)

    def __str__(self) -> str:
        return f"{self.value:.2f} {self.unit}"

    def __repr__(self) -> str:
        return f"Score(value={self.value!r}, unit={self.unit!r})"


@dataclass(frozen=True, slots=True)
class PerformanceMetric:
    """Value object holding aggregate statistical metrics."""
    total_score: Score
    average_score: Score
    highest_score: Score
    lowest_score: Score
    sample_size: int
