from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from omega_research.domain.models import Hypothesis, ExperimentSpec, ExperimentType

DEFAULT_VALIDATION = (
    "REPRODUCIBILITY",
    "LEAKAGE_AUDIT",
    "WALK_FORWARD",
    "COST_ROBUSTNESS",
    "SLIPPAGE_ROBUSTNESS",
    "ADVERSARIAL",
)

def build_plan(
    hypothesis: Hypothesis,
    *,
    parent_strategy_version: str,
    dataset_id: str,
    dataset_hash: str,
    random_seed: int,
    created_at: datetime,
) -> tuple[ExperimentSpec,...]:
    if ExperimentType.BASELINE not in hypothesis.required_experiments:
        required=(ExperimentType.BASELINE,)+hypothesis.required_experiments
    else:
        required=hypothesis.required_experiments

    specs=[]
    baseline_id=None
    for et in required:
        eid=uuid4()
        if et is ExperimentType.BASELINE:
            baseline_id=eid
            config={}
        else:
            config=dict(hypothesis.proposed_change)
        specs.append(ExperimentSpec(
            eid,hypothesis.hypothesis_id,et,hypothesis.strategy_family,
            parent_strategy_version,config,dataset_id,dataset_hash,random_seed,
            DEFAULT_VALIDATION,
            {"cpu_minutes":Decimal("10"),"output_gb":Decimal("0.2")},
            created_at,
            baseline_experiment_id=None if et is ExperimentType.BASELINE else baseline_id,
        ))
    return tuple(specs)

def plan_has_baseline(specs) -> bool:
    return any(s.experiment_type is ExperimentType.BASELINE for s in specs)
