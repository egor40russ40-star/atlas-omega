from __future__ import annotations
from datetime import datetime
from pathlib import Path

def safe_component(v: str | None) -> str:
    if not v:
        return "_none"
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in v)

def partition_path(base: str | Path, *, stream: str, instrument_id: str | None, occurred_at: datetime) -> Path:
    return (
        Path(base)
        / f"stream={safe_component(stream)}"
        / f"instrument={safe_component(instrument_id)}"
        / f"date={occurred_at.date().isoformat()}"
    )
