"""Generic repository infrastructure using TypeVar and Generic."""

from typing import Generic, TypeVar

from sports_app.protocols import Identifiable

# Bound TypeVar constrained to entities that fulfill the Identifiable protocol
TEntity = TypeVar("TEntity", bound=Identifiable)


class InMemoryRepository(Generic[TEntity]):
    """Generic in-memory repository for storing and querying domain entities."""

    def __init__(self) -> None:
        self._items: dict[int, TEntity] = {}

    def add(self, entity: TEntity) -> None:
        """Add or update entity in repository."""
        self._items[entity.id] = entity

    def get(self, entity_id: int) -> TEntity | None:
        """Retrieve entity by primary ID in O(1) time."""
        return self._items.get(entity_id)

    def all(self) -> list[TEntity]:
        """Return all entities currently in storage."""
        return list(self._items.values())

    def remove(self, entity_id: int) -> bool:
        """Remove entity by ID. Returns True if existed."""
        return self._items.pop(entity_id, None) is not None

    def __len__(self) -> int:
        return len(self._items)
