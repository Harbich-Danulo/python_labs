"""Структурні інтерфейси (Protocols) для системи та тест-даблів."""

from collections.abc import Iterable
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from sports_accounting.models import Result


@runtime_checkable
class Identifiable(Protocol):
    """Протокол сутності з унікальним ідентифікатором."""

    @property
    def id(self) -> int:
        ...


@runtime_checkable
class Notifier(Protocol):
    """Протокол для надсилання сповіщень (наприклад, пошта, телеграм, консоль)."""

    def send(self, recipient: str, message: str) -> None:
        ...


@runtime_checkable
class ResultRepository(Protocol):
    """Протокол сховища спортивних результатів."""

    def add(self, result: Result) -> None:
        ...

    def get(self, result_id: int) -> Result | None:
        ...

    def get_all(self) -> list[Result]:
        ...

    def find_by_sport(self, sport_name: str) -> list[Result]:
        ...

    def count(self) -> int:
        ...


@runtime_checkable
class AsyncExternalResultsProvider(Protocol):
    """Асинхронний провайдер зовнішніх результатів з віддаленого API."""

    async def fetch_remote_results(self, sport_name: str) -> list[dict[str, Any]]:
        ...


@runtime_checkable
class ResultExporter(Protocol):
    """Протокол експорту результатів у файл."""

    def export(self, results: Iterable[Result], target_path: Path) -> int:
        ...
