from __future__ import annotations

ELIGIBLE_REGIMES = {
    "TREND_PULLBACK": {"TREND_UP","TREND_DOWN","TRANSITION"},
    "BREAKOUT_RETEST": {"BREAKOUT_UP","BREAKOUT_DOWN","COMPRESSION","TRANSITION"},
    "LIQUIDITY_SWEEP": {"RANGE","TRANSITION","LOW_LIQUIDITY"},
    "COMPRESSION_BREAKOUT": {"COMPRESSION","BREAKOUT_UP","BREAKOUT_DOWN"},
    "ORDERFLOW": {"TREND_UP","TREND_DOWN","RANGE","BREAKOUT_UP","BREAKOUT_DOWN"},
    "ROSN_CORE": {"TREND_UP","TREND_DOWN","RANGE","TRANSITION","BREAKOUT_UP","BREAKOUT_DOWN"},
    "CNYRUBF_BRM": {"TREND_UP","TREND_DOWN","RANGE","TRANSITION","BREAKOUT_UP","BREAKOUT_DOWN"},
    "SCALPER": {"RANGE","TREND_UP","TREND_DOWN","BREAKOUT_UP","BREAKOUT_DOWN"},
}

def regime_eligible(family: str, dominant_regime: str | None) -> bool:
    if dominant_regime is None:
        return False
    allowed = ELIGIBLE_REGIMES.get(family, set())
    return dominant_regime in allowed
