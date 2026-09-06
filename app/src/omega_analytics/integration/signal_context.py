from dataclasses import dataclass
from typing import Optional


@dataclass
class SignalContext:
    """
    Контекст торгового сигнала перед исполнением.
    """

    instrument: str
    strategy: str

    timeframe: str

    market_regime: str
    volatility: str
    volume_state: str

    support_level: Optional[float] = None
    resistance_level: Optional[float] = None

    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    decision: str = "WAIT"
    reason: str = ""