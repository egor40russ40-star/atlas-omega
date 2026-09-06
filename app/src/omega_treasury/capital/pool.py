from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

@dataclass(slots=True)
class CapitalPool:
    pool_id: UUID
    account_id: UUID
    strategy_id: str
    currency: str
    allocated: Decimal = Decimal("0")
    reserved: Decimal = Decimal("0")
    deployed: Decimal = Decimal("0")
    safety_reserve: Decimal = Decimal("0")

    @property
    def available(self) -> Decimal:
        value = self.allocated - self.reserved - self.deployed - self.safety_reserve
        return value

    def reserve(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("reserve amount must be positive")
        if amount > self.available:
            raise ValueError("TREASURY_INSUFFICIENT_AVAILABLE_CAPITAL")
        self.reserved += amount

    def release(self, amount: Decimal) -> None:
        if amount <= 0 or amount > self.reserved:
            raise ValueError("invalid release amount")
        self.reserved -= amount

    def deploy_from_reserve(self, amount: Decimal) -> None:
        if amount <= 0 or amount > self.reserved:
            raise ValueError("invalid deploy amount")
        self.reserved -= amount
        self.deployed += amount

    def close_deployed(self, amount: Decimal) -> None:
        if amount <= 0 or amount > self.deployed:
            raise ValueError("invalid close amount")
        self.deployed -= amount
