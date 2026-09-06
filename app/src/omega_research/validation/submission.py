from __future__ import annotations
from datetime import datetime
from uuid import uuid4
import hashlib,json
from omega_research.domain.models import StrategyCandidate, ValidationSubmission, CandidateState

REQUIRED_GATES = (
    "REPRODUCIBILITY",
    "LEAKAGE_AUDIT",
    "WALK_FORWARD",
    "COST_ROBUSTNESS",
    "SLIPPAGE_ROBUSTNESS",
    "MONTE_CARLO",
    "ADVERSARIAL",
    "SHADOW",
    "SANDBOX",
    "SAFETY_ZERO_VIOLATIONS",
)

def submit_to_validation(
    candidate: StrategyCandidate,
    *,
    digital_twin_plan_id: str,
    submitted_at: datetime,
) -> ValidationSubmission:
    if candidate.state is not CandidateState.LAB:
        raise ValueError("candidate must be LAB")
    manifest_payload={
        "candidate_id":str(candidate.candidate_id),
        "genome_hash":candidate.genome_hash,
        "config_hash":candidate.config_hash,
        "code_hash":candidate.code_hash,
        "validation_plan":candidate.validation_plan,
        "required_gates":REQUIRED_GATES,
        "digital_twin_plan_id":digital_twin_plan_id,
    }
    raw=json.dumps(manifest_payload,sort_keys=True,separators=(",",":"))
    mh=hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return ValidationSubmission(
        uuid4(),candidate.candidate_id,submitted_at,digital_twin_plan_id,
        REQUIRED_GATES,mh,{"reason":"RESEARCH_VALIDATION_SUBMITTED"}
    )
