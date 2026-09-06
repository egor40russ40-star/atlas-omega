from dataclasses import dataclass

@dataclass
class MarketSnapshot:
    symbol: str
    price: float
    volume: float
    spread: float
    support: float | None = None
    resistance: float | None = None
    regime: str = "UNKNOWN"
    volatility: str = "UNKNOWN"

@dataclass
class LiveSignal:
    symbol: str
    action: str
    confidence: str
    reason: str
