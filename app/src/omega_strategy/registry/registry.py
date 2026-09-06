from __future__ import annotations
from omega_strategy.domain.models import StrategyDescriptor

class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies = {}

    def register(self, strategy) -> None:
        sid = strategy.descriptor.strategy_id
        if sid in self._strategies:
            raise ValueError(f"strategy already registered: {sid}")
        self._strategies[sid] = strategy

    def all(self):
        return tuple(self._strategies.values())

    def by_instrument(self, instrument_id: str):
        return tuple(
            s for s in self._strategies.values()
            if s.descriptor.instrument_id in {instrument_id, "*"}
        )

    def get(self, strategy_id: str):
        return self._strategies[strategy_id]
