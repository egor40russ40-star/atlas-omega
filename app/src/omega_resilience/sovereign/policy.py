CRITICAL_LOCAL_COMPONENTS = {
    "CORE",
    "DATA",
    "TREASURY",
    "CAPITAL",
    "RISK",
    "SAFETY",
    "EXECUTION",
    "MEMORY",
    "BLACK_BOX",
    "COMMANDER",
    "RESILIENCE",
}

OPTIONAL_EXTERNAL_COMPONENTS = {
    "REMOTE_AI",
    "CLOUD_BACKUP",
    "REMOTE_DASHBOARD",
}

def sovereign_core_complete(available_components) -> bool:
    return CRITICAL_LOCAL_COMPONENTS.issubset(set(available_components))

def external_failure_blocks_live(component: str) -> bool:
    return component not in OPTIONAL_EXTERNAL_COMPONENTS
