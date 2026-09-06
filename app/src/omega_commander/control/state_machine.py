from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class LocalControlState:
    operational_state: str = "READY"
    safe_pause_active: bool = False
    kill_switch_active: bool = False

    def safe_pause(self) -> tuple[str,...]:
        self.safe_pause_active=True
        return ("CMD_SAFE_PAUSE_ACTIVE",)

    def enter_safe(self) -> tuple[str,...]:
        self.operational_state="SAFE"
        self.safe_pause_active=True
        return ("CMD_ENTERED_SAFE",)

    def emergency_stop(self) -> tuple[str,...]:
        self.operational_state="EMERGENCY"
        self.safe_pause_active=True
        self.kill_switch_active=True
        return ("CMD_EMERGENCY_STOP_ACTIVE",)

    def resume(self) -> tuple[str,...]:
        if self.kill_switch_active:
            raise ValueError("CMD_RESUME_DENIED_KILL_SWITCH")
        if self.operational_state != "READY":
            raise ValueError("CMD_RESUME_DENIED_NOT_READY")
        self.safe_pause_active=False
        return ()
