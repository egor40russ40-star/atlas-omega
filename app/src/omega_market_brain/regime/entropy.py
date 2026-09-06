from __future__ import annotations
from decimal import Decimal
import math

def normalized_entropy(distribution: dict[str, Decimal]) -> Decimal:
    ps = [float(v) for v in distribution.values() if v > 0]
    if len(ps) <= 1:
        return Decimal("0")
    h = -sum(p * math.log(p) for p in ps)
    hmax = math.log(len(distribution))
    return Decimal(str(h / hmax if hmax > 0 else 0))
