from dataclasses import dataclass


@dataclass
class StrategyScore:
    strategy: str

    trades: int
    win_rate: float
    average_r: float
    total_pnl: float

    score: int
    rating: str