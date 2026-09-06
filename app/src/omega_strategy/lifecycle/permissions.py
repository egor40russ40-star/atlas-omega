from __future__ import annotations
from omega_strategy.domain.models import StrategyDescriptor, StrategyRole

def can_produce_live_candidate(descriptor: StrategyDescriptor) -> bool:
    if descriptor.sandbox_only:
        return False
    return descriptor.role is StrategyRole.CHAMPION and descriptor.live_permission

def can_run_shadow(descriptor: StrategyDescriptor) -> bool:
    return descriptor.role in {
        StrategyRole.LAB, StrategyRole.SHADOW, StrategyRole.SANDBOX,
        StrategyRole.CHALLENGER, StrategyRole.CHAMPION
    }

def can_run_sandbox(descriptor: StrategyDescriptor) -> bool:
    return descriptor.role in {
        StrategyRole.SANDBOX, StrategyRole.CHALLENGER, StrategyRole.CHAMPION
    } or descriptor.sandbox_only
