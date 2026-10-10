"""Streaming file reader using generators and yield from."""

from collections.abc import Iterator
from pathlib import Path


def read_lines(path: Path) -> Iterator[str]:
    """Stream lines from a file one-by-one using yield from."""
    with path.open("r", encoding="utf-8") as file:
        yield from file


def clean_lines(lines: Iterator[str]) -> Iterator[str]:
    """Clean and strip whitespace from streaming lines, discarding empty ones."""
    for line in lines:
        cleaned = line.strip()
        if cleaned:
            yield cleaned
