from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from omega_strategy.domain.models import StrategyProposal, StrategyAction, ProposalClass, ScoreComponents

@dataclass(frozen=True, slots=True)
class LegacySignal:
    strategy_id: str
    instrument_id: str
    side: str | None
    entry_price: Decimal | None
    stop_price: Decimal | None
    take_profit_price: Decimal | None
    quantity: Decimal | None
    requested_capital_rub: Decimal | None
    requested_risk_rub: Decimal | None
    confidence: Decimal
    reason_codes: tuple[str,...]
    world_model_id: str
    created_at: datetime


def legacy_signal_to_proposal(x: LegacySignal) -> StrategyProposal:
    if x.side not in {'BUY','SELL'}:
        action=StrategyAction.WAIT; pclass=ProposalClass.WAIT
    else:
        action=StrategyAction.LONG_PROPOSAL if x.side=='BUY' else StrategyAction.SHORT_PROPOSAL
        pclass=ProposalClass.ENTRY
    c=max(Decimal('0'),min(x.confidence,Decimal('1')))
    scores=ScoreComponents(c,c,c,c,c,c,Decimal('0.5'),c,Decimal('1'),Decimal('0'))
    return StrategyProposal(
        uuid4(),x.strategy_id,x.instrument_id,x.created_at,action,pclass,x.side,
        x.entry_price,x.stop_price,x.take_profit_price,x.quantity,
        x.requested_capital_rub,x.requested_risk_rub,c,scores,x.reason_codes,
        x.world_model_id,x.created_at+timedelta(seconds=30),{'source':'LEGACY_ADAPTER'}
    )
