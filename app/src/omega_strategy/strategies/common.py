from __future__ import annotations
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4
from omega_strategy.domain.models import (
    StrategyProposal, StrategyAction, ProposalClass, ScoreComponents
)

def neutral_score(*, setup=0, regime=0, tf=0, of=0, level=0, ctx=0, hist=0.5, exec_ready=0, quality=1, uncertainty=0.5):
    return ScoreComponents(
        Decimal(str(setup)),Decimal(str(regime)),Decimal(str(tf)),
        Decimal(str(of)),Decimal(str(level)),Decimal(str(ctx)),
        Decimal(str(hist)),Decimal(str(exec_ready)),Decimal(str(quality)),
        Decimal(str(uncertainty))
    )

def wait_proposal(descriptor, world_model, context, reasons):
    return StrategyProposal(
        uuid4(), descriptor.strategy_id, descriptor.instrument_id, context.now,
        StrategyAction.WAIT, ProposalClass.WAIT, None, None, None, None,
        None, None, None, Decimal("0"),
        neutral_score(quality=1-float(getattr(world_model.uncertainty,"score",0))),
        tuple(sorted(set(reasons or ["STRAT_WAIT"]))),
        getattr(world_model,"metadata",{}).get("world_model_id","wm"),
        context.now + timedelta(seconds=30),
    )
