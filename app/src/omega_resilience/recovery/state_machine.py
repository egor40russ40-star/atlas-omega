from __future__ import annotations
from dataclasses import dataclass
from omega_resilience.domain.models import RecoveryState

MAIN_PATH = (
    RecoveryState.BOOT,
    RecoveryState.SELF_TEST,
    RecoveryState.BROKER_CONNECT,
    RecoveryState.ACCOUNT_SYNC,
    RecoveryState.POSITION_SYNC,
    RecoveryState.ORDER_SYNC,
    RecoveryState.DATABASE_RECONCILIATION,
    RecoveryState.RISK_REBUILD,
    RecoveryState.MARKET_DATA_HEALTH,
    RecoveryState.SAFE,
    RecoveryState.READY,
    RecoveryState.LIVE,
)

@dataclass(slots=True)
class RecoveryMachine:
    state: RecoveryState = RecoveryState.BOOT

    def transition(self, new_state: RecoveryState) -> None:
        if self.state is RecoveryState.BOOT and new_state is RecoveryState.LIVE:
            raise ValueError("RES_BOOT_TO_LIVE_FORBIDDEN")
        if self.state is RecoveryState.RECOVERY and new_state is RecoveryState.LIVE:
            raise ValueError("RES_RECOVERY_TO_LIVE_FORBIDDEN")
        if self.state in {RecoveryState.SAFE,RecoveryState.EMERGENCY} and new_state is RecoveryState.LIVE:
            raise ValueError("READY required before LIVE")

        if new_state in {RecoveryState.RECOVERY,RecoveryState.EMERGENCY,RecoveryState.SHUTDOWN,RecoveryState.PAUSED,RecoveryState.CAUTION,RecoveryState.DEFENSIVE}:
            self.state=new_state
            return

        if self.state in MAIN_PATH and new_state in MAIN_PATH:
            i=MAIN_PATH.index(self.state)
            j=MAIN_PATH.index(new_state)
            if j == i+1:
                self.state=new_state
                return
            # SAFE may be re-entered from READY/LIVE after issue.
            if new_state is RecoveryState.SAFE and self.state in {RecoveryState.READY,RecoveryState.LIVE}:
                self.state=new_state
                return
        raise ValueError(f"invalid recovery transition: {self.state.value}->{new_state.value}")
