from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Any

@dataclass(frozen=True, slots=True)
class MemoryLineage:
    object_id: str
    object_type: str
    created_at: datetime
    source_mode: str
    source_observation_ids: tuple[str, ...]
    source_outcome_ids: tuple[str, ...] = ()
    replay_run_id: str | None = None
    transform_name: str = ""
    transform_version: str = ""
    config_hash: str = ""
    code_version: str = ""
    metadata: Mapping[str, Any] | None = None

def validate_memory_lineage(x: MemoryLineage) -> None:
    if not x.source_observation_ids:
        raise ValueError("MEMORY_LINEAGE_MISSING")
    if not x.transform_name or not x.transform_version:
        raise ValueError("MEMORY_LINEAGE_MISSING")
