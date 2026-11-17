"""Незмінний Value Object для збереження та порівняння спортивного результату."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Score:
    """Незмінний об'єкт значення спортивного результату."""

    value: float
    unit: str

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError(f"Значення результату не може бути від'ємним: {self.value}")
        if not self.unit or not self.unit.strip():
            raise ValueError("Одиниця вимірювання не може бути порожньою")

    def __add__(self, other: object) -> "Score":
        if not isinstance(other, Score):
            return NotImplemented
        if self.unit != other.unit:
            raise ValueError(f"Неможливо додати результати з різними одиницями: '{self.unit}' != '{other.unit}'")
        return Score(round(self.value + other.value, 4), self.unit)

    def __sub__(self, other: object) -> "Score":
        if not isinstance(other, Score):
            return NotImplemented
        if self.unit != other.unit:
            raise ValueError(f"Неможливо відняти результати з різними одиницями: '{self.unit}' != '{other.unit}'")
        diff = round(self.value - other.value, 4)
        if diff < 0:
            raise ValueError(f"Різниця результатів не може бути від'ємною ({diff})")
        return Score(diff, self.unit)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Score):
            return NotImplemented
        if self.unit != other.unit:
            raise ValueError(f"Неможливо порівняти різні одиниці: '{self.unit}' != '{other.unit}'")
        return self.value < other.value

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Score):
            return NotImplemented
        if self.unit != other.unit:
            raise ValueError(f"Неможливо порівняти різні одиниці: '{self.unit}' != '{other.unit}'")
        return self.value > other.value

    def __str__(self) -> str:
        return f"{self.value:.2f} {self.unit}"
