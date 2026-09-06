from __future__ import annotations
from omega_deploy.domain.models import RuntimeConfig, DeploymentMode, NodeRole


def deployment_reasons(cfg: RuntimeConfig) -> list[str]:
    reasons=[]
    if cfg.mode is DeploymentMode.LIVE:
        reasons.append("DEPLOY_LIVE_HARD_LOCKED")
    if cfg.live_enabled:
        reasons.append("DEPLOY_LIVE_HARD_LOCKED")
    if not cfg.live_hard_locked:
        reasons.append("DEPLOY_LIVE_LOCK_MISSING")

    if cfg.mode is DeploymentMode.OFFLINE_FAKE and cfg.broker_network_enabled:
        reasons.append("DEPLOY_OFFLINE_NETWORK_FORBIDDEN")
    if cfg.mode is DeploymentMode.OFFLINE_FAKE and cfg.broker_adapter != "FAKE":
        reasons.append("DEPLOY_FAKE_BROKER_REQUIRED")
    if cfg.mode in {DeploymentMode.SANDBOX, DeploymentMode.SHADOW} and cfg.broker_adapter == "REAL_LIVE":
        reasons.append("DEPLOY_LIVE_BROKER_FORBIDDEN")

    if cfg.node_role is NodeRole.RESEARCH_NODE:
        if cfg.execution_process_enabled:
            reasons.append("DEPLOY_RESEARCH_EXECUTION_FORBIDDEN")
        if cfg.broker_write_enabled:
            reasons.append("DEPLOY_RESEARCH_BROKER_WRITE_FORBIDDEN")
        if cfg.broker_token_allowed or cfg.broker_secret_ref is not None:
            reasons.append("DEPLOY_RESEARCH_BROKER_TOKEN_FORBIDDEN")
        if cfg.production_db_write_enabled:
            reasons.append("DEPLOY_RESEARCH_PROD_DB_WRITE_FORBIDDEN")
        if not cfg.research_enabled:
            reasons.append("DEPLOY_RESEARCH_DISABLED")
        if cfg.broker_network_enabled:
            reasons.append("DEPLOY_RESEARCH_BROKER_NETWORK_FORBIDDEN")
        if cfg.data_access not in {"LOCAL_ONLY","LOCAL_OR_REPLICATED_READ_ONLY","REPLICATED_READ_ONLY"}:
            reasons.append("DEPLOY_RESEARCH_DATA_ACCESS_INVALID")

    if cfg.node_role is NodeRole.LIVE_NODE and cfg.research_enabled:
        reasons.append("DEPLOY_LIVE_NODE_RESEARCH_FORBIDDEN")

    if cfg.remote_access not in {"LOCAL_ONLY","LAN_ONLY","VPN_ONLY","REMOTE_DISABLED"}:
        reasons.append("DEPLOY_REMOTE_POLICY_INVALID")
    return sorted(set(reasons))


def assert_deployment_safe(cfg: RuntimeConfig) -> None:
    reasons=deployment_reasons(cfg)
    if reasons:
        raise ValueError(",".join(reasons))
