from __future__ import annotations
from typing import Protocol, Iterable, Mapping
from omega_market_brain.domain.models import Candle, OrderFlowState, ContextNode

class MarketDataPort(Protocol):
    def candles(self, instrument_id: str, timeframe: str, limit: int) -> Iterable[Candle]:
        ...

    def orderflow_state(self, instrument_id: str) -> OrderFlowState | None:
        ...

class ContextDataPort(Protocol):
    def context_nodes(self, instrument_id: str) -> Iterable[ContextNode]:
        ...
