from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class StressScenario:
    name: str
    commission_multiplier: Decimal = Decimal("1")
    slippage_multiplier: Decimal = Decimal("1")
    latency_ms_add: int = 0
    fill_fraction_multiplier: Decimal = Decimal("1")
    spread_multiplier: Decimal = Decimal("1")
    drop_event_probability: Decimal = Decimal("0")
    disconnect: bool = False
    timeout_after_acceptance: bool = False

def standard_scenarios() -> tuple[StressScenario,...]:
    return (
        StressScenario("BASELINE"),
        StressScenario("COST_X2",commission_multiplier=Decimal("2")),
        StressScenario("SLIPPAGE_X2",slippage_multiplier=Decimal("2")),
        StressScenario("LATENCY_300MS",latency_ms_add=300),
        StressScenario("LOW_LIQUIDITY",fill_fraction_multiplier=Decimal("0.5"),spread_multiplier=Decimal("2")),
        StressScenario("BROKER_TIMEOUT_AFTER_ACCEPT",timeout_after_acceptance=True),
        StressScenario("DISCONNECT",disconnect=True),
    )
