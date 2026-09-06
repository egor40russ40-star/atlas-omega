from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class CostModel:
    commission_rate: Decimal = Decimal("0")
    fixed_fee: Decimal = Decimal("0")
    minimum_fee: Decimal = Decimal("0")
    version: str = "cost-v1"

    def commission(self, notional: Decimal) -> Decimal:
        fee = abs(notional) * self.commission_rate + self.fixed_fee
        return max(fee, self.minimum_fee)
