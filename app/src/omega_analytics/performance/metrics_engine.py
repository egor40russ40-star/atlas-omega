from dataclasses import dataclass


@dataclass
class PerformanceReport:
    trades: int
    wins: int
    losses: int

    win_rate: float
    total_pnl: float
    average_r: float
    profit_factor: float


class MetricsEngine:
    """
    Расчёт статистики по серии сделок.
    """

    def calculate(self, trades):

        total = len(trades)

        if total == 0:
            return PerformanceReport(
                trades=0,
                wins=0,
                losses=0,
                win_rate=0.0,
                total_pnl=0.0,
                average_r=0.0,
                profit_factor=0.0,
            )


        wins = [
            t for t in trades
            if t.status == "WIN"
        ]

        losses = [
            t for t in trades
            if t.status == "LOSS"
        ]


        total_pnl = sum(
            t.pnl for t in trades
        )


        average_r = (
            sum(t.r_multiple for t in trades)
            / total
        )


        gross_profit = sum(
            t.pnl for t in wins
        )


        gross_loss = abs(
            sum(t.pnl for t in losses)
        )


        if gross_loss > 0:
            profit_factor = (
                gross_profit /
                gross_loss
            )
        else:
            profit_factor = 0.0


        return PerformanceReport(
            trades=total,

            wins=len(wins),
            losses=len(losses),

            win_rate=round(
                len(wins) / total * 100,
                2
            ),

            total_pnl=round(
                total_pnl,
                2
            ),

            average_r=round(
                average_r,
                2
            ),

            profit_factor=round(
                profit_factor,
                2
            ),
        )