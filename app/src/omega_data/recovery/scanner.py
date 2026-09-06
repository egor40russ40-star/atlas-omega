from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class RecoveryScan:
    stale_temp_files: tuple[Path, ...]
    manifest_files: tuple[Path, ...]
    data_files: tuple[Path, ...]

def scan_storage(base: str | Path) -> RecoveryScan:
    base = Path(base)
    temps = []
    manifests = []
    data = []
    if not base.exists():
        return RecoveryScan((), (), ())
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if ".tmp." in p.name:
            temps.append(p)
        elif p.name.endswith(".manifest.json"):
            manifests.append(p)
        else:
            data.append(p)
    return RecoveryScan(tuple(sorted(temps)), tuple(sorted(manifests)), tuple(sorted(data)))
