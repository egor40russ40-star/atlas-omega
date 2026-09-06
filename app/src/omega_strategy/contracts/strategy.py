from __future__ import annotations
from typing import Protocol, Any
from omega_strategy.domain.models import StrategyDescriptor, StrategyContext, StrategyProposal

class Strategy(Protocol):
    @property
    def descriptor(self) -> StrategyDescriptor:
        ...

    def evaluate(self, world_model: Any, context: StrategyContext) -> StrategyProposal:
        ...
