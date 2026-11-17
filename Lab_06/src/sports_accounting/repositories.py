"""Реалізація репозиторію результатів у пам'яті."""

from sports_accounting.exceptions import RepositoryError
from sports_accounting.models import Result
from sports_accounting.protocols import ResultRepository


class InMemoryResultRepository(ResultRepository):
    """Сховище спортивних результатів у пам'яті."""

    def __init__(self) -> None:
        self._items: dict[int, Result] = {}

    def add(self, result: Result) -> None:
        if result.id in self._items:
            raise RepositoryError(f"Результат з ID {result.id} вже існує у сховищі")
        self._items[result.id] = result

    def get(self, result_id: int) -> Result | None:
        return self._items.get(result_id)

    def get_all(self) -> list[Result]:
        return list(self._items.values())

    def find_by_sport(self, sport_name: str) -> list[Result]:
        target = sport_name.strip().lower()
        return [r for r in self._items.values() if r.sport.name.strip().lower() == target]

    def count(self) -> int:
        return len(self._items)
