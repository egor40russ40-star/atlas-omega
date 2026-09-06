from __future__ import annotations
from decimal import Decimal

def compression_score(current_atr_pct: Decimal | None, baseline_atr_pct: Decimal | None) -> Decimal:
    if current_atr_pct is None or baseline_atr_pct is None or baseline_atr_pct <= 0:
        return Decimal("0")
    ratio = current_atr_pct / baseline_atr_pct
    if ratio >= 1:
        return Decimal("0")
    score = Decimal("1") - ratio
    return max(Decimal("0"), min(score, Decimal("1")))
