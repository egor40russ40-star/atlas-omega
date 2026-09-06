from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json
from omega_data.storage.atomic_file import atomic_write_bytes
from omega_data.archive.checksum import sha256_file

@dataclass(frozen=True, slots=True)
class SegmentManifest:
    segment_id: str
    state: str
    data_path: str
    checksum_sha256: str
    row_count: int
    created_at: str
    min_occurred_at: str | None
    max_occurred_at: str | None
    transform_version: str | None = None

def build_manifest(
    *,
    segment_id: str,
    data_path: str | Path,
    row_count: int,
    min_occurred_at: str | None,
    max_occurred_at: str | None,
    transform_version: str | None = None,
) -> SegmentManifest:
    p = Path(data_path)
    return SegmentManifest(
        segment_id=segment_id,
        state="CLOSED",
        data_path=str(p),
        checksum_sha256=sha256_file(p),
        row_count=row_count,
        created_at=datetime.now(timezone.utc).isoformat(),
        min_occurred_at=min_occurred_at,
        max_occurred_at=max_occurred_at,
        transform_version=transform_version,
    )

def write_manifest(path: str | Path, manifest: SegmentManifest) -> Path:
    data = (json.dumps(asdict(manifest), ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    return atomic_write_bytes(path, data)
