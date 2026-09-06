from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from omega_strategy.domain.models import StrategyProposal, RouterDecision

@dataclass(frozen=True, slots=True)
class TradeIntentCandidate:
    intent_id: UUID
    proposal_id: UUID
    strategy_id: str
    instrument_id: str
    side: str
    quantity: Decimal
    entry_price: Decimal | None
    stop_price: Decimal | None
    take_profit_price: Decimal | None
    requested_capital_rub: Decimal
    requested_risk_rub: Decimal
    created_at: datetime
    world_model_id: str

def build_trade_intent_candidate(
    proposal: StrategyProposal,
    decision: RouterDecision,
    *,
    now: datetime,
) -> TradeIntentCandidate:
    if decision.selected_proposal_id != proposal.proposal_id:
        raise ValueError("router decision does not select proposal")
    if not decision.live_candidate:
        raise ValueError("STRAT_LIVE_PERMISSION_DENIED")
    if proposal.side not in {"BUY","SELL"}:
        raise ValueError("proposal has no executable side")
    if proposal.requested_quantity is None or proposal.requested_capital_rub is None or proposal.requested_risk_rub is None:
        raise ValueError("proposal missing capital/risk/quantity")
    return TradeIntentCandidate(
        uuid4(), proposal.proposal_id, proposal.strategy_id, proposal.instrument_id,
        proposal.side, proposal.requested_quantity, proposal.entry_price,
        proposal.stop_price, proposal.take_profit_price,
        proposal.requested_capital_rub, proposal.requested_risk_rub, now,
        proposal.world_model_id
    )
