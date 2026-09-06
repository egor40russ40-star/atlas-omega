from .models import ReplayReport


class ReplayEngine:
    """
    Движок повторного прогона торговых результатов.
    """

    def build_report(
        self,
        *,
        strategy: str,
        trades: list,
    ) -> ReplayReport:

        total = len(trades)

        wins = sum(
            1
            for trade in trades
            if trade.status == "WIN"
        )

        losses = sum(
            1
            for trade in trades
            if trade.status == "LOSS"
        )

        total_pnl = round(
            sum(
                trade.pnl
                for trade in trades
            ),
            2,
        )

        average_r = 0

        if total:
            average_r = round(
                sum(
                    trade.r_multiple
                    for trade in trades
                )
                / total,
                2,
            )

        win_rate = 0

        if total:
            win_rate = round(
                wins / total * 100,
                2,
            )

        return ReplayReport(
            strategy=strategy,
            trades=total,
            wins=wins,
            losses=losses,
            total_pnl=total_pnl,
            average_r=average_r,
            win_rate=win_rate,
        )