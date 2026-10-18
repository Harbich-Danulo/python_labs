"""Protocols and structural interfaces for dependency inversion (SOLID DIP)."""

from typing import Protocol, runtime_checkable

from sports_app.value_objects import Score


@runtime_checkable
class Identifiable(Protocol):
    """Protocol for any domain entity having an integer ID."""
    @property
    def id(self) -> int:
        ...


@runtime_checkable
class ScoredEntity(Protocol):
    """Protocol for any entity that contains a performance Score."""
    @property
    def score(self) -> Score:
        ...


class Notifier(Protocol):
    """Protocol for notification delivery (email, console, SMS, webhook)."""
    def send(self, recipient: str, message: str) -> None:
        ...


class ResultExporter(Protocol):
    """Protocol for exporting domain data to external destinations."""
    def export(self, title: str, content: str) -> str:
        ...
