from __future__ import annotations
from datetime import datetime
from uuid import uuid4
import json,hashlib
from omega_research.domain.models import (
    Hypothesis, StrategyGenome, StrategyCandidate, CandidateState
)
from omega_research.genetics.hash import genome_hash

def _hash_obj(x) -> str:
    raw=json.dumps(x,sort_keys=True,separators=(",",":"),default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def build_candidate(
    *,
    hypothesis: Hypothesis,
    genome: StrategyGenome,
    parent_versions: tuple[str,...],
    code_hash: str,
    created_at: datetime,
    validation_plan: tuple[str,...],
) -> StrategyCandidate:
    changes=tuple({
        "parameter":m.parameter,
        "old":str(m.old_value),
        "new":str(m.new_value),
        "type":m.mutation_type,
    } for m in genome.mutation_history)
    return StrategyCandidate(
        uuid4(),hypothesis.hypothesis_id,genome.family,parent_versions,
        genome.generation,genome_hash(genome),
        _hash_obj({k:str(v) for k,v in genome.parameters.items()}),
        code_hash,CandidateState.LAB,created_at,changes,validation_plan,
        {"live_permission":False,"broker_write":False}
    )
