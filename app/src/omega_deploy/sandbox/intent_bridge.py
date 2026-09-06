from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from omega_strategy.router.trade_intent_builder import TradeIntentCandidate
from omega_strategy.domain.models import ProposalClass
from omega_deploy.domain.models import DeploymentMode

def build_sandbox_intent(proposal,decision,*,mode: DeploymentMode,now: datetime) -> TradeIntentCandidate:
    if mode is DeploymentMode.LIVE:
        raise ValueError("DEPLOY_LIVE_HARD_LOCKED")
    if decision.selected_proposal_id != proposal.proposal_id:
        raise ValueError("SANDBOX_PROPOSAL_NOT_SELECTED")
    if proposal.proposal_class not in {ProposalClass.ENTRY,ProposalClass.HEDGE,ProposalClass.EXIT,ProposalClass.PROTECTIVE}:
        raise ValueError("SANDBOX_NONEXECUTABLE_PROPOSAL")
    if proposal.side not in {"BUY","SELL"}:
        raise ValueError("SANDBOX_SIDE_MISSING")
    if proposal.requested_quantity is None or proposal.requested_capital_rub is None or proposal.requested_risk_rub is None:
        raise ValueError("SANDBOX_INTENT_INCOMPLETE")
    return TradeIntentCandidate(
        uuid4(),proposal.proposal_id,proposal.strategy_id,proposal.instrument_id,
        proposal.side,proposal.requested_quantity,proposal.entry_price,
        proposal.stop_price,proposal.take_profit_price,
        proposal.requested_capital_rub,proposal.requested_risk_rub,now,
        proposal.world_model_id
    )
