from typing import Dict, List

from .models import TradeRecord


class TradeJournal:
    def __init__(self):
        self._trades: Dict[str, TradeRecord] = {}

    def add_trade(self, trade: TradeRecord) -> None:
        self._trades[trade.trade_id] = trade

    def update_trade(self, trade: TradeRecord) -> None:
        self._trades[trade.trade_id] = trade

    def get_trade(self, trade_id: str) -> TradeRecord | None:
        return self._trades.get(trade_id)

    def get_history(self) -> List[TradeRecord]:
        return list(self._trades.values())

    def count(self) -> int:
        return len(self._trades)