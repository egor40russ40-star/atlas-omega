from __future__ import annotations
from uuid import UUID
from omega_memory.domain.models import MarketObservation

class ImmutableObservationStore:
    """Reference in-memory contract. Production adapter will use PostgreSQL/Parquet."""
    def __init__(self) -> None:
        self._items: dict[UUID, MarketObservation] = {}

    def add(self, observation: MarketObservation) -> None:
        existing = self._items.get(observation.observation_id)
        if existing is not None:
            if existing != observation:
                raise ValueError("MEMORY_OBSERVATION_IMMUTABLE")
            return
        self._items[observation.observation_id] = observation

    def get(self, observation_id: UUID) -> MarketObservation:
        return self._items[observation_id]

    def all(self) -> tuple[MarketObservation, ...]:
        return tuple(self._items.values())
