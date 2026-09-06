from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SignalRecord:
    instrument: str
    strategy: str
    timeframe: str
    market_regime: str
    volatility: str
    volume_state: str
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    signal_reason: str = ""


@dataclass
class TradeRecord:
    trade_id: str
    instrument: str
    strategy: str
    side: str

    entry_price: float
    quantity: float

    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    exit_price: Optional[float] = None

    commission: float = 0.0
    slippage: float = 0.0

    pnl: Optional[float] = None
    r_multiple: Optional[float] = None

    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None

    exit_reason: Optional[str] = None