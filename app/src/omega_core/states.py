from enum import Enum

class OmegaState(str, Enum):
    BOOT = "BOOT"
    SELF_TEST = "SELF_TEST"
    BROKER_SYNC = "BROKER_SYNC"
    RECONCILIATION = "RECONCILIATION"
    SAFE = "SAFE"
    READY = "READY"
    LIVE = "LIVE"
    CAUTION = "CAUTION"
    DEFENSIVE = "DEFENSIVE"
    PAUSED = "PAUSED"
    RECOVERY = "RECOVERY"
    EMERGENCY = "EMERGENCY"
    SHUTDOWN = "SHUTDOWN"

ALLOWED_TRANSITIONS: dict[OmegaState, set[OmegaState]] = {
    OmegaState.BOOT: {OmegaState.SELF_TEST, OmegaState.EMERGENCY},
    OmegaState.SELF_TEST: {OmegaState.BROKER_SYNC, OmegaState.SAFE, OmegaState.EMERGENCY},
    OmegaState.BROKER_SYNC: {OmegaState.RECONCILIATION, OmegaState.RECOVERY, OmegaState.EMERGENCY},
    OmegaState.RECONCILIATION: {OmegaState.SAFE, OmegaState.RECOVERY, OmegaState.EMERGENCY},
    OmegaState.SAFE: {OmegaState.READY, OmegaState.PAUSED, OmegaState.RECOVERY, OmegaState.SHUTDOWN},
    OmegaState.READY: {OmegaState.LIVE, OmegaState.PAUSED, OmegaState.RECOVERY, OmegaState.SHUTDOWN},
    OmegaState.LIVE: {OmegaState.CAUTION, OmegaState.DEFENSIVE, OmegaState.PAUSED, OmegaState.RECOVERY, OmegaState.EMERGENCY},
    OmegaState.CAUTION: {OmegaState.LIVE, OmegaState.DEFENSIVE, OmegaState.PAUSED, OmegaState.RECOVERY, OmegaState.EMERGENCY},
    OmegaState.DEFENSIVE: {OmegaState.CAUTION, OmegaState.PAUSED, OmegaState.RECOVERY, OmegaState.EMERGENCY},
    OmegaState.PAUSED: {OmegaState.SAFE, OmegaState.READY, OmegaState.RECOVERY, OmegaState.SHUTDOWN},
    OmegaState.RECOVERY: {OmegaState.BROKER_SYNC, OmegaState.SAFE, OmegaState.EMERGENCY},
    OmegaState.EMERGENCY: {OmegaState.RECOVERY, OmegaState.SHUTDOWN},
    OmegaState.SHUTDOWN: set(),
}
