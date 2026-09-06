from __future__ import annotations
from dataclasses import replace
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from omega_deploy.domain.models import DeploymentMode,SandboxRunResult,SandboxRunState
from omega_deploy.config.runtime import read_runtime_config
from omega_deploy.sandbox.fake_broker import FakeBrokerExecutionPort,FakeBrokerFaultPlan
from omega_deploy.sandbox.fixtures import world,account_and_pool,risk_context,risk_limits,instrument_rules
from omega_deploy.sandbox.intent_bridge import build_sandbox_intent
from omega_deploy.sandbox.storage import SandboxJournal
from omega_strategy.adapters.rosn_core import ROSNCoreStrategy
from omega_strategy.adapters.cnyrubf_brm import CNYRUBFBRMStrategy
from omega_strategy.domain.models import StrategyContext,StrategyAction
from omega_strategy.registry.registry import StrategyRegistry
from omega_strategy.router.meta_router import MetaRouter
from omega_integration.pipeline import IntegratedTradePipeline
from omega_resilience.recovery.state_machine import RecoveryMachine,MAIN_PATH
from omega_resilience.domain.models import RecoveryState
from omega_resilience.recovery.readiness import ReadinessInput,ready_allowed

def _strategy(instrument_id: str):
    if instrument_id=="ROSN":
        return ROSNCoreStrategy()
    if instrument_id=="CNYRUBF":
        return CNYRUBFBRMStrategy()
    raise ValueError("SANDBOX_INSTRUMENT_UNSUPPORTED")

def _boot_to_ready():
    m=RecoveryMachine()
    # Stop at SAFE, then explicit readiness gate, then READY. Never LIVE.
    for s in MAIN_PATH[1:MAIN_PATH.index(RecoveryState.READY)]:
        m.transition(s)
    x=ReadinessInput(True,True,True,True,True,True,True,True,False,True,True,True)
    if not ready_allowed(x):
        raise ValueError("SANDBOX_READINESS_FAILED")
    m.transition(RecoveryState.READY)
    return m

def run_offline_sandbox(
    runtime_config_path: str | Path,
    *,
    instrument_id: str,
    bias: str="LONG",
    fault_status=None,
    requested_borrowed_increment_rub: Decimal=Decimal("0"),
    borrowed_long_rub: Decimal=Decimal("0"),
) -> SandboxRunResult:
    cfg=read_runtime_config(runtime_config_path)
    if cfg.mode is not DeploymentMode.OFFLINE_FAKE:
        raise ValueError("SANDBOX_OFFLINE_FAKE_REQUIRED")

    run_id=str(uuid4())
    now=datetime.now(timezone.utc)
    journal=SandboxJournal(cfg.sandbox_db)
    journal.append_event(run_id,"RUN_CREATED",{"instrument":instrument_id},occurred_at=now)

    try:
        _boot_to_ready()
        journal.append_event(run_id,"READY",{"state":"READY","live":False},occurred_at=datetime.now(timezone.utc))

        strategy=_strategy(instrument_id)
        w=world(instrument_id,bias)
        ctx=StrategyContext(
            datetime.now(timezone.utc),
            "CNYRUBF_DEDICATED" if instrument_id=="CNYRUBF" else "ROSN_PRIMARY",
            Decimal("0"),None,Decimal("10000"),Decimal("0"),
        )
        proposal=strategy.evaluate(w,ctx)
        if proposal.action is StrategyAction.WAIT:
            result=SandboxRunResult(
                run_id,instrument_id,SandboxRunState.COMPLETED,"STRATEGY_WAIT",
                None,None,proposal.reason_codes,
                "Стратегия выбрала WAIT; торговый запрос не создавался.",
                {"live":False}
            )
            journal.save_run(run_id,instrument_id,result.state.value,result.stage,result.__dict__ if hasattr(result,"__dict__") else {
                "run_id":result.run_id,"stage":result.stage,"reason_codes":result.reason_codes
            },created_at=now)
            return result

        reg=StrategyRegistry(); reg.register(strategy)
        decision=MetaRouter(reg).route([proposal])
        # In offline sandbox we require selection, but NOT live_candidate.
        if decision.selected_proposal_id is None:
            result=SandboxRunResult(
                run_id,instrument_id,SandboxRunState.COMPLETED,"ROUTER_WAIT",
                None,None,decision.reason_codes,
                "Meta Router выбрал WAIT.",
                {"live":False}
            )
            journal.save_run(run_id,instrument_id,result.state.value,result.stage,{
                "run_id":run_id,"reason_codes":result.reason_codes
            },created_at=now)
            return result

        intent=build_sandbox_intent(proposal,decision,mode=cfg.mode,now=ctx.now)
        account,pool=account_and_pool(instrument_id,intent.strategy_id)

        fault=None
        if fault_status is not None:
            fault=FakeBrokerFaultPlan(next_submit_status=fault_status)
        broker=FakeBrokerExecutionPort(fault)
        pipe=IntegratedTradePipeline(broker_port=broker,risk_limits=risk_limits())
        rc=risk_context(borrowed_long=str(borrowed_long_rub))
        pipeline=pipe.submit(
            intent,account=account,pool=pool,risk_context=rc,
            instrument_rules=instrument_rules(instrument_id),
            broker_state_snapshot_id="fake-broker-state-1",
            system_state="READY",reconciliation_status="OK",
            market_data_fresh=True,broker_state_fresh=True,
            requested_borrowed_increment_rub=requested_borrowed_increment_rub,
        )
        rec=pipeline.execution_record
        result=SandboxRunResult(
            run_id,instrument_id,SandboxRunState.COMPLETED,
            pipeline.stage,
            None if rec is None else rec.state.value,
            None if rec is None else rec.broker_order_id,
            pipeline.reason_codes,
            "Offline Sandbox завершён без доступа к реальному брокеру.",
            {"live":False,"broker_calls":len(broker.calls),"mode":cfg.mode.value}
        )
        journal.save_run(run_id,instrument_id,result.state.value,result.stage,{
            "run_id":result.run_id,"instrument_id":result.instrument_id,
            "state":result.state.value,"stage":result.stage,
            "execution_state":result.execution_state,
            "broker_order_id":result.broker_order_id,
            "reason_codes":list(result.reason_codes),
            "message_ru":result.message_ru,
            "metadata":dict(result.metadata),
        },created_at=now)
        journal.append_event(run_id,"RUN_COMPLETED",{
            "stage":result.stage,"execution_state":result.execution_state,
            "reason_codes":list(result.reason_codes)
        },occurred_at=datetime.now(timezone.utc))
        return result
    except Exception as e:
        result=SandboxRunResult(
            run_id,instrument_id,SandboxRunState.FAILED,"EXCEPTION",
            None,None,("SANDBOX_EXCEPTION",),f"Sandbox завершился ошибкой: {type(e).__name__}",
            {"live":False,"error":str(e)}
        )
        journal.save_run(run_id,instrument_id,result.state.value,result.stage,{
            "error":str(e),"reason_codes":["SANDBOX_EXCEPTION"]
        },created_at=now)
        return result
    finally:
        journal.close()
