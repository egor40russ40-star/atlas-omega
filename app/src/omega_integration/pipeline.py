from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from omega_common.hashing import canonical_hash
from omega_treasury.types import CapitalRequest, CapitalDecisionStatus, AccountRecord
from omega_treasury.capital.governor import CapitalGovernor
from omega_treasury.capital.pool import CapitalPool
from omega_risk.domain.models import RiskRequest, RiskContext, RiskLimits, RiskDecisionStatus
from omega_risk.hierarchy.governor import RiskGovernor
from omega_risk.safety.authorization import issue_authorization
from omega_risk.safety.kernel import SafetyContext, authorized, safety_reasons
from omega_execution.domain.models import ExecutionRequest, InstrumentRules, OrderState
from omega_execution.normalization.rules import normalize_quantity, normalize_price
from omega_execution.idempotency.key import make_key
from omega_execution.broker.engine import ExecutionEngine

@dataclass(frozen=True, slots=True)
class PipelineResult:
    stage: str
    reason_codes: tuple[str,...]
    capital_decision: object | None = None
    risk_decision: object | None = None
    authorization: object | None = None
    execution_record: object | None = None

class IntegratedTradePipeline:
    """Fail-closed bridge between Strategy output and Execution.

    REDUCED Capital/Risk decisions are deliberately not auto-resized in v100 assembly.
    They require a fresh quantity/price calculation and a new intent/approval chain.
    """
    def __init__(self, *, broker_port, capital_limits=None, risk_limits: RiskLimits | None=None):
        self.capital=CapitalGovernor(**(capital_limits or {}))
        self.risk=RiskGovernor(risk_limits or RiskLimits())
        self.execution=ExecutionEngine(broker_port)

    def submit(
        self,
        intent,
        *, account: AccountRecord, pool: CapitalPool, risk_context: RiskContext,
        instrument_rules: InstrumentRules, broker_state_snapshot_id: str,
        system_state: str='READY', reconciliation_status: str='OK',
        market_data_fresh: bool=True, broker_state_fresh: bool=True,
        requested_borrowed_increment_rub: Decimal=Decimal('0'), order_style: str='LIMIT',
    ) -> PipelineResult:
        if intent.requested_capital_rub is None or intent.requested_risk_rub is None or intent.quantity is None:
            return PipelineResult('INTENT_INVALID',('INTEGRATION_INTENT_INCOMPLETE',))

        cap_req=CapitalRequest(
            uuid4(),intent.strategy_id,account.internal_account_id,intent.instrument_id,
            intent.requested_capital_rub,intent.requested_risk_rub,requested_borrowed_increment_rub,'ENTRY'
        )
        cap=self.capital.decide(
            cap_req,account,pool,
            current_borrowed_long_rub=risk_context.current_borrowed_long_rub,
            current_borrowed_hedge_rub=risk_context.current_borrowed_hedge_rub,
            margin_classification_known=True,
        )
        if cap.status is CapitalDecisionStatus.DENIED:
            return PipelineResult('CAPITAL_DENIED',cap.reason_codes,capital_decision=cap)
        if cap.status is CapitalDecisionStatus.REDUCED:
            return PipelineResult('REQUOTE_REQUIRED',('INTEGRATION_REQUOTE_REQUIRED',)+cap.reason_codes,capital_decision=cap)

        risk_req=RiskRequest(
            uuid4(),intent.intent_id,intent.strategy_id,str(account.internal_account_id),account.role.value,
            intent.instrument_id,intent.side,cap.approved_risk,cap.approved_capital,
            cap.approved_borrowed_increment,intent.world_model_id,
        )
        rd=self.risk.decide(risk_req,risk_context)
        if rd.status is RiskDecisionStatus.DENIED:
            return PipelineResult('RISK_DENIED',rd.reason_codes,cap,rd)
        if rd.status is RiskDecisionStatus.REDUCED:
            return PipelineResult('REQUOTE_REQUIRED',('INTEGRATION_REQUOTE_REQUIRED',)+rd.reason_codes,cap,rd)

        qty=normalize_quantity(intent.quantity,instrument_rules)
        limit_price=None
        if order_style!='MARKET' and intent.entry_price is not None:
            limit_price=normalize_price(intent.entry_price,instrument_rules)

        cap_hash=canonical_hash(cap)
        risk_hash=canonical_hash(rd)
        now=datetime.now(timezone.utc)
        valid_until=min(rd.valid_until, intent.created_at.replace(tzinfo=intent.created_at.tzinfo) if False else rd.valid_until)
        auth=issue_authorization(
            intent_id=intent.intent_id,account_id=account.broker_account_id,
            instrument_id=intent.instrument_id,side=intent.side,quantity=qty,order_style=order_style,
            limit_price=limit_price,capital_decision_hash=cap_hash,risk_decision_hash=risk_hash,
            market_snapshot_id=intent.world_model_id,broker_state_snapshot_id=broker_state_snapshot_id,
            issued_at=now,valid_until=rd.valid_until,
        )
        sctx=SafetyContext(system_state,reconciliation_status,market_data_fresh,broker_state_fresh,risk_context.kill_switch)
        s_reasons=safety_reasons(auth,sctx,now=now)
        if s_reasons:
            return PipelineResult('SAFETY_DENIED',tuple(s_reasons),cap,rd,auth)

        key=make_key(
            intent_id=str(intent.intent_id),broker_account_id=account.broker_account_id,
            instrument_id=intent.instrument_id,side=intent.side,quantity=qty,order_style=order_style,
            limit_price=limit_price,stop_price=intent.stop_price,approval_chain_hash=auth.authorization_hash,
        )
        req=ExecutionRequest(
            uuid4(),intent.intent_id,account.broker_account_id,intent.instrument_id,intent.side,qty,
            order_style,now,auth.valid_until,auth.authorization_hash,key,
            limit_price=limit_price,stop_price=intent.stop_price,market_snapshot_id=intent.world_model_id,
            metadata={'strategy_id':intent.strategy_id,'capital_hash':cap_hash,'risk_hash':risk_hash},
        )
        rec=self.execution.submit(req,approvals_ok=True,broker_state_fresh=broker_state_fresh)
        reasons=() if rec.state in {OrderState.ACCEPTED,OrderState.FILLED,OrderState.PARTIALLY_FILLED} else ((rec.last_message,) if rec.last_message else ())
        return PipelineResult('EXECUTION',tuple(reasons),cap,rd,auth,rec)
