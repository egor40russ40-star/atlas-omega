from __future__ import annotations
from dataclasses import dataclass,field

START_ORDER=(
    "omega-safety",
    "omega-risk",
    "omega-capital",
    "omega-broker-state",
    "omega-market-data",
    "omega-execution",
    "omega-treasury",
    "omega-recorder",
    "omega-brain",
    "omega-strategies",
    "omega-dashboard",
    "omega-news",
    "omega-replay",
    "omega-research",
    "omega-ai-lab",
)

@dataclass
class ReferenceServiceManager:
    states: dict[str,str]=field(default_factory=dict)
    operations: list[tuple[str,str]]=field(default_factory=list)

    def start_all(self):
        for s in START_ORDER:
            self.states[s]="RUNNING"
            self.operations.append(("START",s))
        return tuple(START_ORDER)

    def stop_all(self):
        for s in reversed(START_ORDER):
            self.states[s]="STOPPED"
            self.operations.append(("STOP",s))
        return tuple(reversed(START_ORDER))

    def status(self):
        return dict(self.states)
