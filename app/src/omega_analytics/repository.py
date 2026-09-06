from datetime import datetime

from .models import TradeRecord, SignalRecord
from .storage import AnalyticsStorage


class AnalyticsRepository:

    def __init__(self, storage: AnalyticsStorage):
        self.storage = storage

    def save_trade(self, trade: TradeRecord):

        query = """
        INSERT INTO trades (
            symbol,
            strategy,
            side,
            entry_price,
            exit_price,
            quantity,
            pnl,
            commission,
            slippage,
            r_multiple,
            entry_time,
            exit_time,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.storage.execute(
            query,
            (
                trade.instrument,
                trade.strategy,
                trade.side,
                trade.entry_price,
                trade.exit_price,
                trade.quantity,
                trade.pnl,
                trade.commission,
                trade.slippage,
                trade.r_multiple,
                str(trade.entry_time),
                str(trade.exit_time),
                trade.exit_reason,
            ),
        )

    def save_signal(self, signal: SignalRecord):

        query = """
        INSERT INTO signals (
            symbol,
            strategy,
            timeframe,
            regime,
            volatility,
            reason,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        self.storage.execute(
            query,
            (
                signal.instrument,
                signal.strategy,
                signal.timeframe,
                signal.market_regime,
                signal.volatility,
                signal.reason,
                datetime.utcnow().isoformat(),
            ),
        )