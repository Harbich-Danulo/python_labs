"""Доменні сутності та колекція RankingTable (Варіант 9)."""

from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from sports_accounting.value_objects import Score


@dataclass(frozen=True, slots=True)
class Athlete:
    """Сутність спортсмена."""

    id: int
    name: str
    country: str = "Україна"
    age: int = 20

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise ValueError(f"ID спортсмена повинен бути додатнім: {self.id}")
        if not self.name or not self.name.strip():
            raise ValueError("Ім'я спортсмена не може бути порожнім")
        if not (10 <= self.age <= 100):
            raise ValueError(f"Вік спортсмена повинен бути в межах [10, 100]: {self.age}")


@dataclass(frozen=True, slots=True)
class Sport:
    """Сутність спортивної дисципліни."""

    id: int
    name: str
    unit: str
    is_lower_better: bool = False

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise ValueError(f"ID виду спорту повинен бути додатнім: {self.id}")
        if not self.name or not self.name.strip():
            raise ValueError("Назва виду спорту не може бути порожньою")


@dataclass(frozen=True, slots=True)
class Competition:
    """Сутність змагання / турніру."""

    id: int
    name: str
    location: str
    year: int

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise ValueError(f"ID змагання має бути додатнім: {self.id}")
        if not self.name or not self.name.strip():
            raise ValueError("Назва змагання не може бути порожньою")
        if not (1900 <= self.year <= 2100):
            raise ValueError(f"Рік змагання має бути в межах [1900, 2100]: {self.year}")


@dataclass(frozen=True, slots=True)
class Result:
    """Центральна сутність спортивного результату."""

    id: int
    athlete: Athlete
    sport: Sport
    competition: Competition
    score: Score
    category: str
    timestamp: datetime

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise ValueError(f"ID результату повинен бути додатнім: {self.id}")
        if not self.category or not self.category.strip():
            raise ValueError("Категорія не може бути порожньою")
        if self.score.unit != self.sport.unit:
            raise ValueError(
                f"Одиниця вимірювання результату '{self.score.unit}' не відповідає виду спорту '{self.sport.unit}'"
            )

    def to_dict(self) -> dict[str, Any]:
        """Серіалізація сутності у формат словника."""
        return {
            "id": self.id,
            "athlete": {
                "id": self.athlete.id,
                "name": self.athlete.name,
                "country": self.athlete.country,
                "age": self.athlete.age,
            },
            "sport": {
                "id": self.sport.id,
                "name": self.sport.name,
                "unit": self.sport.unit,
                "is_lower_better": self.sport.is_lower_better,
            },
            "competition": {
                "id": self.competition.id,
                "name": self.competition.name,
                "location": self.competition.location,
                "year": self.competition.year,
            },
            "score": {
                "value": self.score.value,
                "unit": self.score.unit,
            },
            "category": self.category,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class RankingEntry:
    """Рядок турнірної таблиці із врахуванням розділеного рангу."""

    rank: int
    result: Result


class RankingTable:
    """Контейнер турнірної таблиці з ранжуванням та обробкою нічиїх (ties)."""

    def __init__(self, sport: Sport, results: list[Result]) -> None:
        self.sport = sport
        # Фільтруємо за видом спорту
        sport_results = [r for r in results if r.sport.name == sport.name]
        # Сортуємо результати (менше чи більше краще)
        sorted_results = sorted(
            sport_results,
            key=lambda r: r.score.value,
            reverse=not sport.is_lower_better,
        )

        self._entries: list[RankingEntry] = []
        if not sorted_results:
            return

        current_rank = 1
        for i, res in enumerate(sorted_results):
            if i > 0:
                prev_res = sorted_results[i - 1]
                if res.score.value == prev_res.score.value:
                    # Однаковий результат -> однаковий ранг
                    pass
                else:
                    current_rank = i + 1
            self._entries.append(RankingEntry(rank=current_rank, result=res))

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[RankingEntry]:
        return iter(self._entries)

    def __getitem__(self, index: int) -> RankingEntry:
        return self._entries[index]

    def __contains__(self, athlete_name: object) -> bool:
        if not isinstance(athlete_name, str):
            return False
        return any(entry.result.athlete.name == athlete_name for entry in self._entries)

    def __repr__(self) -> str:
        return f"RankingTable(sport={self.sport.name!r}, entries_count={len(self._entries)})"
