from __future__ import annotations
from dataclasses import replace
from uuid import UUID
from omega_treasury.types import AccountRecord, AccountRole, AccountState

class AccountRegistry:
    def __init__(self) -> None:
        self._by_id: dict[UUID, AccountRecord] = {}
        self._by_broker_id: dict[str, UUID] = {}

    def add_discovered(self, record: AccountRecord) -> None:
        if record.broker_account_id in self._by_broker_id:
            raise ValueError("account already exists")
        safe = replace(record, role=AccountRole.UNASSIGNED, state=AccountState.UNASSIGNED)
        self._by_id[safe.internal_account_id] = safe
        self._by_broker_id[safe.broker_account_id] = safe.internal_account_id

    def assign_role(self, account_id: UUID, role: AccountRole, *, system_safe: bool) -> AccountRecord:
        if not system_safe:
            raise ValueError("account assignment requires SAFE/PAUSED state")
        current = self._by_id[account_id]
        updated = replace(current, role=role, state=AccountState.ASSIGNED)
        self._by_id[account_id] = updated
        return updated

    def enable(self, account_id: UUID, *, reconciled: bool) -> AccountRecord:
        if not reconciled:
            raise ValueError("account must be reconciled before enable")
        current = self._by_id[account_id]
        if current.role is AccountRole.UNASSIGNED:
            raise ValueError("unassigned account cannot be enabled")
        updated = replace(current, state=AccountState.ENABLED)
        self._by_id[account_id] = updated
        return updated

    def get(self, account_id: UUID) -> AccountRecord:
        return self._by_id[account_id]
