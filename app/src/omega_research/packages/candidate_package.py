from __future__ import annotations
from pathlib import Path
import json,hashlib
from omega_research.domain.models import StrategyCandidate

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def create_candidate_package(
    candidate: StrategyCandidate,
    *,
    output_dir: str | Path,
    parent_info: dict,
    config: dict,
) -> Path:
    base=Path(output_dir)/f"candidate-{candidate.candidate_id}"
    if base.exists():
        raise ValueError("RESEARCH_PACKAGE_IMMUTABLE")
    base.mkdir(parents=True)
    files={
        "manifest.json":{
            "candidate_id":str(candidate.candidate_id),
            "family":candidate.family,
            "genome_hash":candidate.genome_hash,
            "config_hash":candidate.config_hash,
            "code_hash":candidate.code_hash,
            "state":candidate.state.value,
            "validation_plan":candidate.validation_plan,
        },
        "parent.json":parent_info,
        "config.json":config,
        "change_set.json":list(candidate.changes),
    }
    for name,payload in files.items():
        (base/name).write_text(json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    checks={p.name:_sha256(p) for p in sorted(base.iterdir()) if p.is_file()}
    (base/"checksums.json").write_text(json.dumps(checks,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return base
