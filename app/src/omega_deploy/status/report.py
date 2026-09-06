from __future__ import annotations
from pathlib import Path
from omega_deploy.config.runtime import read_runtime_config
from omega_deploy.sandbox.storage import SandboxJournal


def status_payload(config_path: str | Path):
    cfg=read_runtime_config(config_path)
    j=SandboxJournal(cfg.sandbox_db)
    try:
        runs=j.latest_runs(5)
    finally:
        j.close()
    return {
        "node_role":cfg.node_role.value,
        "mode":cfg.mode.value,
        "live_enabled":cfg.live_enabled,
        "live_hard_locked":cfg.live_hard_locked,
        "execution_process_enabled":cfg.execution_process_enabled,
        "broker_write_enabled":cfg.broker_write_enabled,
        "broker_token_allowed":cfg.broker_token_allowed,
        "production_db_write_enabled":cfg.production_db_write_enabled,
        "research_enabled":cfg.research_enabled,
        "data_access":cfg.data_access,
        "broker_adapter":cfg.broker_adapter,
        "network_enabled":cfg.broker_network_enabled,
        "runtime":cfg.runtime_dir,
        "recent_sandbox_runs":runs,
    }


def status_ru(config_path: str | Path) -> str:
    x=status_payload(config_path)
    lines=[
        "ATLAS OMEGA v100 — СТАТУС УСТАНОВКИ",
        f"Роль узла: {x['node_role']}",
        f"Режим: {x['mode']}",
        f"Research: {'ВКЛЮЧЁН' if x['research_enabled'] else 'ВЫКЛЮЧЕН'}",
        f"LIVE: {'ВКЛЮЧЁН' if x['live_enabled'] else 'ЗАБЛОКИРОВАН'}",
        f"Hard Lock LIVE: {'ДА' if x['live_hard_locked'] else 'НЕТ'}",
        f"LIVE/Broker Execution process: {'РАЗРЕШЁН' if x['execution_process_enabled'] else 'ЗАБЛОКИРОВАН'}",
        f"Запись брокеру: {'РАЗРЕШЕНА' if x['broker_write_enabled'] else 'ЗАБЛОКИРОВАНА'}",
        f"Broker token: {'РАЗРЕШЁН' if x['broker_token_allowed'] else 'ЗАПРЕЩЁН'}",
        f"Запись в production DB: {'РАЗРЕШЕНА' if x['production_db_write_enabled'] else 'ЗАБЛОКИРОВАНА'}",
        f"Доступ к данным: {x['data_access']}",
        f"Broker adapter: {x['broker_adapter']}",
        f"Сетевой доступ брокера: {'ДА' if x['network_enabled'] else 'НЕТ'}",
        f"Runtime: {x['runtime']}",
        f"Последних sandbox-запусков: {len(x['recent_sandbox_runs'])}",
    ]
    for r in x["recent_sandbox_runs"][:3]:
        lines.append(f"- {r['instrument_id']}: {r['stage']} / {r['state']}")
    return "\n".join(lines)
