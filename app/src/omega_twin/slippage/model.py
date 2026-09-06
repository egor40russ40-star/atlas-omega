from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class SlippageModel:
    base_bps: Decimal = Decimal("0")
    volatility_bps_multiplier: Decimal = Decimal("0")
    liquidity_bps_multiplier: Decimal = Decimal("0")
    version: str = "slippage-v1"

    def slippage_bps(
        self,
        *,
        volatility_score: Decimal = Decimal("0"),
        liquidity_penalty: Decimal = Decimal("0"),
    ) -> Decimal:
        return (
            self.base_bps
            + self.volatility_bps_multiplier * volatility_score
            + self.liquidity_bps_multiplier * liquidity_penalty
        )

    def apply(self, price: Decimal, *, side: str, volatility_score: Decimal = Decimal("0"), liquidity_penalty: Decimal = Decimal("0")) -> tuple[Decimal, Decimal]:
        bps = self.slippage_bps(volatility_score=volatility_score, liquidity_penalty=liquidity_penalty)
        frac = bps / Decimal("10000")
        slip = price * frac
        filled = price + slip if side == "BUY" else price - slip
        return filled, abs(slip)
