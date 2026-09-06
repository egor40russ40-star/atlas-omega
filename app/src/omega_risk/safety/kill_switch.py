from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(slots=True)
class KillSwitch:
    active: bool = False
    reason: str | None = None
    changed_at: datetime | None = None

    def activate(self, reason: str) -> None:
        self.active = True
        self.reason = reason
        self.changed_at = datetime.now(timezone.utc)

    def clear(self, *, system_safe: bool, reconciliation_ok: bool) -> None:
        if not system_safe or not reconciliation_ok:
            raise ValueError("kill switch can only be cleared after SAFE + reconciliation")
        self.active = False
        self.reason = None
        self.changed_at = datetime.now(timezone.utc)
