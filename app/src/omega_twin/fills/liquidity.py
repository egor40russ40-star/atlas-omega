from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class FillLiquidityModel:
    max_fill_fraction: Decimal = Decimal("1")
    participation_rate: Decimal = Decimal("1")

    def fillable_quantity(self, *, requested_remaining: Decimal, bar_volume: Decimal) -> Decimal:
        cap_by_fraction = requested_remaining * self.max_fill_fraction
        cap_by_volume = bar_volume * self.participation_rate
        return max(Decimal("0"), min(requested_remaining, cap_by_fraction, cap_by_volume))
