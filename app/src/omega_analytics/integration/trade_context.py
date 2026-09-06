from dataclasses import dataclass
from typing import Optional


@dataclass
class TradeContext:
    """
    Полный контекст исполнения сделки.
    """

    instrument: str
    strategy: str

    side: str

    entry_price: float
    quantity: float

    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    exit_price: Optional[float] = None

    pnl: Optional[float] = None
    r_multiple: Optional[float] = None

    status: str = "OPEN"

    error_tag: Optional[str] = None