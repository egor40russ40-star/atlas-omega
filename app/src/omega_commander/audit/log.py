from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True, slots=True)
class CommandAuditEvent:
    audit_id: UUID
    occurred_at: datetime
    command_id: UUID
    command_type: str
    principal_id: str
    role: str
    client_type: str
    command_hash: str
    confirmation_id: UUID | None
    state: str
    reason_codes: tuple[str,...]
    system_state_before: str
    system_state_after: str
    correlation_id: UUID

class AppendOnlyAudit:
    def __init__(self):
        self._events=[]

    def append(self,event: CommandAuditEvent):
        self._events.append(event)

    def all(self):
        return tuple(self._events)

    def delete(self,*args,**kwargs):
        raise ValueError("CMD_AUDIT_APPEND_ONLY")

    def replace(self,*args,**kwargs):
        raise ValueError("CMD_AUDIT_APPEND_ONLY")
