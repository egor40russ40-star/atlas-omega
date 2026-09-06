from __future__ import annotations
import argparse
from pathlib import Path
from omega_deploy.install.installer import initialize
from omega_deploy.sandbox.harness import run_offline_sandbox
from omega_deploy.status.report import status_ru
from omega_deploy.domain.models import NodeRole


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def setup_main(argv=None):
    p=argparse.ArgumentParser(description="ATLAS OMEGA — установка GMKtec RESEARCH NODE")
    p.add_argument("--runtime",default="./runtime")
    p.add_argument("--non-interactive",action="store_true")
    args=p.parse_args(argv)
    result=initialize(repo_root(),Path(args.runtime),node_role=NodeRole.RESEARCH_NODE)
    print(result.message_ru)
    if result.config_path:
        print("Роль узла: RESEARCH_NODE")
        print("Конфигурация:",result.config_path)
        print("Следующий шаг: python scripts/omega_status.py --config ""+str(result.config_path)+""")
    if not result.ok:
        print("Причины:",", ".join(result.reason_codes))
        return 2
    return 0


def sandbox_main(argv=None):
    p=argparse.ArgumentParser(description="ATLAS OMEGA — Offline Fake Research Sandbox")
    p.add_argument("--config",default="./runtime/atlas_omega.runtime.json")
    p.add_argument("--instrument",choices=["ROSN","CNYRUBF"],default="ROSN")
    p.add_argument("--bias",choices=["LONG","SHORT"],default="LONG")
    args=p.parse_args(argv)
    r=run_offline_sandbox(args.config,instrument_id=args.instrument,bias=args.bias)
    print(f"{r.instrument_id}: {r.stage}")
    print(f"Execution: {r.execution_state or '—'}")
    print(r.message_ru)
    if r.reason_codes:
        print("Причины:",", ".join(r.reason_codes))
    return 0 if r.state.value!="FAILED" else 2


def status_main(argv=None):
    p=argparse.ArgumentParser(description="ATLAS OMEGA — статус Research Node")
    p.add_argument("--config",default="./runtime/atlas_omega.runtime.json")
    args=p.parse_args(argv)
    print(status_ru(args.config))
    return 0
