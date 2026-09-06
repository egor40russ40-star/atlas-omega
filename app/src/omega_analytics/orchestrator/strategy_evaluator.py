from .models import StrategyScore


class StrategyEvaluator:
    """
    Оценка качества стратегии по результатам replay.
    """

    def evaluate(self, report):

        score = 0

        if report.win_rate >= 60:
            score += 30

        if report.average_r >= 0.5:
            score += 30

        if report.total_pnl > 0:
            score += 20

        if report.trades >= 50:
            score += 20

        if score >= 80:
            rating = "A"

        elif score >= 60:
            rating = "B"

        else:
            rating = "C"


        return StrategyScore(
            strategy=report.strategy,

            trades=report.trades,
            win_rate=report.win_rate,
            average_r=report.average_r,
            total_pnl=report.total_pnl,

            score=score,
            rating=rating,
        )