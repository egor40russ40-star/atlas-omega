from __future__ import annotations
from typing import Protocol, Iterable
from omega_treasury.types import BrokerMoneySnapshot

class BrokerTreasuryPort(Protocol):
    def list_accounts(self) -> Iterable[dict]:
        ...

    def get_money_snapshot(self, broker_account_id: str) -> BrokerMoneySnapshot:
        ...

    def list_cash_operations(self, broker_account_id: str, *, since_cursor: str | None = None) -> Iterable[dict]:
        ...

    def get_margin_snapshot(self, broker_account_id: str) -> dict:
        ...
