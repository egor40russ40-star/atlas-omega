from omega_analytics.integration.signal_context import SignalContext


class CNYRUBFAnalyticsAdapter:
    """
    Адаптер CNYRUBF_BRM_V3 → Analytics Pipeline
    """

    strategy_name = "CNYRUBF_BRM_V3"

    def build_signal(
        self,
        *,
        decision: str,
        price: float,
        support: float | None = None,
        resistance: float | None = None,
        stop_loss: float | None = None,
        take_profit: float | None = None,
        timeframe: str = "5m",
        regime: str = "UNKNOWN",
        volatility: str = "UNKNOWN",
        volume_state: str = "UNKNOWN",
        reason: str = "",
    ) -> SignalContext:

        return SignalContext(
            instrument="CNYRUBF",
            strategy=self.strategy_name,

            timeframe=timeframe,

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