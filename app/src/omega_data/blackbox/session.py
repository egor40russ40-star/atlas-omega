from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json
from omega_data.recorder.ring_buffer import RingBuffer, BufferedEvent
from omega_data.storage.atomic_file import atomic_write_bytes
from omega_data.archive.checksum import sha256_file

SECRET_KEYS = {"token", "api_token", "authorization", "password", "secret"}

def _sanitize(value):
    if isinstance(value, dict):
        return {
            k: ("***REDACTED***" if k.lower() in SECRET_KEYS else _sanitize(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [_sanitize(v) for v in value]
    if isinstance(value, tuple):
        return [_sanitize(v) for v in value]
    return value

@dataclass(frozen=True, slots=True)
class BlackBoxCapture:
    session_id: str
    trigger: str
    path: str
    checksum: str
    event_count: int
    captured_at: datetime

def capture_ring_buffer(
    ring: RingBuffer,
    *,
    trigger: str,
    output_dir: str | Path,
) -> BlackBoxCapture:
    session_id = uuid4().hex
    captured_at = datetime.now(timezone.utc)
    rows = []
    for e in ring.snapshot():
        rows.append({
            "occurred_at": e.occurred_at.isoformat(),
            "event_type": e.event_type,
            "payload": _sanitize(e.payload),
            "approx_bytes": e.approx_bytes,
        })
    body = {
        "session_id": session_id,
        "trigger": trigger,
        "captured_at": captured_at.isoformat(),
        "events": rows,
    }
    path = Path(output_dir) / f"blackbox-{captured_at.strftime('%Y%m%dT%H%M%S')}-{session_id}.json"
    atomic_write_bytes(path, (json.dumps(body, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    checksum = sha256_file(path)
    return BlackBoxCapture(session_id, trigger, str(path), checksum, len(rows), captured_at)
