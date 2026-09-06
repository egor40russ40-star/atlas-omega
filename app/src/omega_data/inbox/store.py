from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

@dataclass(frozen=True, slots=True)
class InboxReceipt:
    consumer_name: str
    event_id: UUID
    processed_at: datetime

class InMemoryInbox:
    """Reference deduplication model. Production adapter will use PostgreSQL UNIQUE constraint."""
    def __init__(self) -> None:
        self._seen: set[tuple[str, UUID]] = set()

    def begin(self, consumer_name: str, event_id: UUID) -> bool:
        key = (consumer_name, event_id)
        if key in self._seen:
            return False
        self._seen.add(key)
        return True

    def seen(self, consumer_name: str, event_id: UUID) -> bool:
        return (consumer_name, event_id) in self._seen
