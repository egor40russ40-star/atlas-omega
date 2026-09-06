from dataclasses import dataclass


@dataclass
class BacktestTrade:
    symbol: str
    strategy: str

    entry_price: float
    exit_price: float

    quantity: int

    stop_loss: float
    take_profit: float

    pnl: float
    r_multiple: float

    status: str