from dataclasses import dataclass


@dataclass
class ResearchRecord:
    strategy: str

    trades: int
    wins: int
    losses: int

    total_pnl: float
    average_r: float
    win_rate: float