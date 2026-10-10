"""Data models for sports results streaming."""

from typing import NamedTuple


class SportsRecord(NamedTuple):
    """Immutable data record representing an athlete's performance in a stream."""
    athlete: str
    sport: str
    result: float
    category: str
    timestamp: str


class SportsRangeIterator:
    """Custom iterator object illustrating the iterator protocol (__iter__, __next__, StopIteration)."""

    def __init__(self, start: int, stop: int) -> None:
        self.current = start
        self.stop = stop

    def __iter__(self) -> "SportsRangeIterator":
        return self

    def __next__(self) -> int:
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value


class SportsRange:
    """Custom iterable container that separates the iterable from its iterator."""

    def __init__(self, start: int, stop: int) -> None:
        self.start = start
        self.stop = stop

    def __iter__(self) -> SportsRangeIterator:
        return SportsRangeIterator(self.start, self.stop)
