from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
import json
from omega_deploy.config.runtime import default_runtime_config, write_runtime_config
from omega_deploy.preflight.checks import run_preflight
from omega_deploy.domain.models import NodeRole

@dataclass(frozen=True, slots=True)
class InstallResult:
    ok: bool
    runtime_dir: str
    config_path: str | None
    reason_codes: tuple[str,...]
    message_ru: str


def initialize(repo_root: str | Path, runtime_dir: str | Path, *, node_role: NodeRole = NodeRole.RESEARCH_NODE) -> InstallResult:
    repo=Path(repo_root)
    runtime=Path(runtime_dir)

    # This physical-build installer is deliberately Research Node only.
    if node_role is not NodeRole.RESEARCH_NODE:
        return InstallResult(
            False,str(runtime),None,("DEPLOY_PROFILE_NOT_AVAILABLE",),
            "Эта сборка устанавливается только как OMEGA RESEARCH NODE."
        )

    pre=run_preflight(repo)
    if not pre.passed:
        return InstallResult(
            False,str(runtime),None,pre.blocking_reason_codes,
            "Предварительная проверка не пройдена."
        )

    dirs=[
        runtime,
        runtime/"data",
        runtime/"logs",
        runtime/"state",
        runtime/"reports",
        runtime/"backups",
        runtime/"snapshots",
        runtime/"research",
        runtime/"research"/"datasets",
        runtime/"research"/"parquet",
        runtime/"research"/"duckdb",
        runtime/"research"/"replay",
        runtime/"research"/"backtests",
        runtime/"research"/"experiments",
        runtime/"research"/"models",
        runtime/"research"/"validation_queue",
    ]
    for d in dirs:
        d.mkdir(parents=True,exist_ok=True)

    cfg=default_runtime_config(runtime)
    cfg_path=write_runtime_config(cfg,runtime/"atlas_omega.runtime.json")
    (runtime/"state"/"deployment.json").write_text(json.dumps({
        "stage":"INITIALIZED",
        "node_role":cfg.node_role.value,
        "mode":cfg.mode.value,
        "live_enabled":False,
        "broker_write_enabled":False,
        "production_db_write_enabled":False,
        "research_enabled":True,
        "created_at":datetime.now(timezone.utc).isoformat(),
        "message_ru":"ATLAS OMEGA RESEARCH NODE подготовлен. LIVE/брокерская запись/production DB write заблокированы.",
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return InstallResult(
        True,str(runtime),str(cfg_path),(),
        "OMEGA RESEARCH NODE подготовлен. LIVE и брокерская запись аппаратно-политически заблокированы конфигурацией."
    )
