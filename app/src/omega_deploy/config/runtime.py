from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import json
from omega_deploy.domain.models import RuntimeConfig, DeploymentMode, NodeRole
from omega_deploy.config.guard import assert_deployment_safe


def default_runtime_config(runtime_dir: str | Path) -> RuntimeConfig:
    """Fail-closed default for the physical GMKtec Research Node."""
    r=Path(runtime_dir)
    return RuntimeConfig(
        node_role=NodeRole.RESEARCH_NODE,
        mode=DeploymentMode.OFFLINE_FAKE,
        runtime_dir=str(r),
        data_dir=str(r/"data"),
        logs_dir=str(r/"logs"),
        sandbox_db=str(r/"data"/"sandbox.sqlite3"),
        broker_adapter="FAKE",
        broker_network_enabled=False,
        broker_secret_ref=None,
        live_enabled=False,
        live_hard_locked=True,
        execution_process_enabled=False,
        broker_write_enabled=False,
        broker_token_allowed=False,
        production_db_write_enabled=False,
        research_enabled=True,
        data_access="LOCAL_OR_REPLICATED_READ_ONLY",
        commander_bind="127.0.0.1",
        remote_access="LOCAL_ONLY",
        metadata={
            "deployment_stage":"RESEARCH_NODE_INSTALL_CANDIDATE",
            "node_identity":"GMKTEC_RESEARCH",
            "role_isolation":"HARD_FAIL_CLOSED",
        },
    )


def write_runtime_config(cfg: RuntimeConfig, path: str | Path) -> Path:
    assert_deployment_safe(cfg)
    p=Path(path)
    p.parent.mkdir(parents=True,exist_ok=True)
    payload=asdict(cfg)
    payload["node_role"]=cfg.node_role.value
    payload["mode"]=cfg.mode.value
    p.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return p


def read_runtime_config(path: str | Path) -> RuntimeConfig:
    x=json.loads(Path(path).read_text(encoding="utf-8"))
    if "node_role" not in x:
        raise ValueError("DEPLOY_NODE_ROLE_MISSING")
    cfg=RuntimeConfig(
        node_role=NodeRole(x["node_role"]),
        mode=DeploymentMode(x["mode"]),
        runtime_dir=x["runtime_dir"],
        data_dir=x["data_dir"],
        logs_dir=x["logs_dir"],
        sandbox_db=x["sandbox_db"],
        broker_adapter=x["broker_adapter"],
        broker_network_enabled=bool(x["broker_network_enabled"]),
        broker_secret_ref=x.get("broker_secret_ref"),
        live_enabled=bool(x["live_enabled"]),
        live_hard_locked=bool(x["live_hard_locked"]),
        execution_process_enabled=bool(x.get("execution_process_enabled",False)),
        broker_write_enabled=bool(x.get("broker_write_enabled",False)),
        broker_token_allowed=bool(x.get("broker_token_allowed",False)),
        production_db_write_enabled=bool(x.get("production_db_write_enabled",False)),
        research_enabled=bool(x.get("research_enabled",False)),
        data_access=x.get("data_access","UNSPECIFIED"),
        commander_bind=x["commander_bind"],
        remote_access=x["remote_access"],
        metadata=x.get("metadata",{}),
    )
    assert_deployment_safe(cfg)
    return cfg
