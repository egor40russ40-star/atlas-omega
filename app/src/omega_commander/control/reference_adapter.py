from __future__ import annotations
from omega_commander.control.state_machine import LocalControlState

class ReferenceControlAdapter:
    """Только contract-test adapter. Не управляет реальными сервисами."""
    def __init__(self,state: LocalControlState | None = None):
        self.state=state or LocalControlState()
        self.restarted=[]
        self.acked=[]

    def safe_pause(self):
        return self.state.safe_pause()

    def enter_safe(self):
        return self.state.enter_safe()

    def emergency_stop(self):
        return self.state.emergency_stop()

    def resume(self):
        return self.state.resume()

    def restart_service(self,service_name: str):
        self.restarted.append(service_name)
        return ()

    def acknowledge_incident(self,incident_id: str):
        self.acked.append(incident_id)
        return ()
