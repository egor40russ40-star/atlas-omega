from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

@dataclass(frozen=True, slots=True)
class LineageRecord:
    output_id: str
    output_checksum: str
    created_at: datetime
    transform_name: str
    transform_version: str
    config_hash: str
    code_version: str
    source_event_ids: Tuple[str, ...] = ()
    source_segment_ids: Tuple[str, ...] = ()
    lineage_type: str = "DERIVED"

def validate_lineage(record: LineageRecord) -> None:
    if not record.source_event_ids and not record.source_segment_ids:
        raise ValueError("DATA_LINEAGE_MISSING")
    if not record.transform_name or not record.transform_version:
        raise ValueError("DATA_LINEAGE_MISSING")
