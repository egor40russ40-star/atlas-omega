from dataclasses import dataclass


@dataclass
class ReplayReport:
    strategy: str

    trades: int
    wins: int
    losses: int

    total_pnl: float
    average_r: float

    win_rate: float