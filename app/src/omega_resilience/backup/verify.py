from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from omega_resilience.domain.models import BackupRecord

def sha256_file(path: str | Path) -> str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            b=f.read(1024*1024)
            if not b: break
            h.update(b)
    return h.hexdigest()

def backup_reasons(
    record: BackupRecord | None,
    *,
    now: datetime,
    max_age_hours: int = 24,
    max_restore_verification_age_days: int = 7,
) -> tuple[str,...]:
    if record is None:
        return ("RES_BACKUP_MISSING",)
    r=[]
    p=Path(record.path)
    if not p.exists():
        r.append("RES_BACKUP_MISSING")
    else:
        if sha256_file(p) != record.checksum_sha256:
            r.append("RES_BACKUP_CHECKSUM_FAILED")
    if now-record.created_at > timedelta(hours=max_age_hours):
        r.append("RES_BACKUP_MISSING")
    if (
        record.restore_tested_at is None
        or not record.restore_test_passed
        or now-record.restore_tested_at > timedelta(days=max_restore_verification_age_days)
    ):
        r.append("RES_RESTORE_TEST_STALE")
    return tuple(sorted(set(r)))
