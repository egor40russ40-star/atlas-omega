from .models import DecisionResult


class DecisionEngine:
    """
    Движок оценки качества торгового решения.
    """

    def evaluate(
        self,
        *,
        pattern_win_rate: float,
        average_r: float,
        regime: str,
        volume_confirmed: bool,
        risk_reward: float,
    ):

        score = 0
        reasons = []

        if pattern_win_rate >= 60:
            score += 30
            reasons.append(
                "strong_pattern_history"
            )

        elif pattern_win_rate >= 50:
            score += 15


        if average_r >= 1:
            score += 25
            reasons.append(
                "positive_average_r"
            )


        if volume_confirmed:
            score += 20
            reasons.append(
                "volume_confirmed"
            )


        if risk_reward >= 2:
            score += 25
            reasons.append(
                "good_risk_reward"
            )


        if score >= 75:
            action = "ALLOW"
            confidence = "HIGH"

        elif score >= 50:
            action = "WATCH"
            confidence = "MEDIUM"

        else:
            action = "REJECT"
            confidence = "LOW"


        return DecisionResult(
            action=action,
            score=score,
            reasons=reasons,
            confidence=confidence,
        )