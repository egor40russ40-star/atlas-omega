from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional
from omega_data.domain.models import EventEnvelope

@dataclass(slots=True)
class OutboxRecord:
    event: EventEnvelope
    created_at: datetime
    published_at: Optional[datetime] = None
    publish_attempts: int = 0
    last_error: Optional[str] = None

class InMemoryOutbox:
    """Reference model for contract tests. Production adapter will use PostgreSQL."""
    def __init__(self) -> None:
        self._records: dict[UUID, OutboxRecord] = {}

    def add(self, event: EventEnvelope) -> None:
        if event.event_id in self._records:
            return
        self._records[event.event_id] = OutboxRecord(event, datetime.now(timezone.utc))

    def pending(self) -> list[OutboxRecord]:
        return [r for r in self._records.values() if r.published_at is None]

    def mark_attempt(self, event_id: UUID, error: str | None = None) -> None:
        r = self._records[event_id]
        r.publish_attempts += 1
        r.last_error = error

    def mark_published(self, event_id: UUID) -> None:
        r = self._records[event_id]
        r.published_at = datetime.now(timezone.utc)
        r.last_error = None
