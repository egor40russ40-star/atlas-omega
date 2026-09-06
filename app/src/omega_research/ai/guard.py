from __future__ import annotations

ALLOWED_OUTPUT_TYPES = {
    "HYPOTHESIS_DRAFT",
    "LOG_CLASSIFICATION",
    "EXPERIMENT_DRAFT",
    "PATTERN_CANDIDATE",
    "PARAMETER_PROPOSAL",
    "RESEARCH_SUMMARY",
}

FORBIDDEN_ACTION_TOKENS = (
    "live_write",
    "broker_order",
    "kill_switch_override",
    "risk_override",
    "safety_override",
    "champion_replace",
)

def validate_ai_output(payload: dict) -> None:
    t=payload.get("type")
    if t not in ALLOWED_OUTPUT_TYPES:
        raise ValueError("RESEARCH_AI_OUTPUT_REJECTED")
    action=str(payload.get("action","")).lower()
    if any(tok in action for tok in FORBIDDEN_ACTION_TOKENS):
        raise ValueError("RESEARCH_AI_OUTPUT_REJECTED")
