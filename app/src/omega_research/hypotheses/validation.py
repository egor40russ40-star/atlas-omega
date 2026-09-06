from __future__ import annotations
from omega_research.domain.models import Hypothesis

def hypothesis_reasons(h: Hypothesis) -> list[str]:
    reasons=[]
    if len(h.problem_statement.strip()) < 20:
        reasons.append("RESEARCH_HYPOTHESIS_NOT_FALSIFIABLE")
    if len(h.expected_mechanism.strip()) < 15:
        reasons.append("RESEARCH_HYPOTHESIS_NOT_FALSIFIABLE")
    if len(h.falsifiable_prediction.strip()) < 15:
        reasons.append("RESEARCH_HYPOTHESIS_NOT_FALSIFIABLE")
    if not h.target_metrics:
        reasons.append("RESEARCH_HYPOTHESIS_NOT_FALSIFIABLE")
    if not h.required_experiments:
        reasons.append("RESEARCH_HYPOTHESIS_NOT_FALSIFIABLE")
    return sorted(set(reasons))
