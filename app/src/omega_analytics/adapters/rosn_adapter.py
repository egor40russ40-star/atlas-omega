from omega_analytics.integration.signal_context import SignalContext


class ROSNAnalyticsAdapter:
    """
    Адаптер ROSN_HEDGE_V3 → Analytics Pipeline
    """

    strategy_name = "ROSN_HEDGE_V3"

    def build_signal(
        self,
        *,
        decision: str,
        price: float,
        support: float | None = None,
        resistance: float | None = None,
        stop_loss: float | None = None,
        take_profit: float | None = None,
        regime: str = "UNKNOWN",
        volatility: str = "UNKNOWN",
        volume_state: str = "UNKNOWN",
        reason: str = "",
    ) -> SignalContext:

        return SignalContext(
            instrument="ROSN",
            strategy=self.strategy_name,

            timeframe="5m",

            market_regime=regime,
            volatility=volatility,
            volume_state=volume_state,

            support_level=support,
            resistance_level=resistance,

            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,

            decision=decision,
            reason=reason,
        )