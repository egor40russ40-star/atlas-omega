from __future__ import annotations
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4
from omega_strategy.domain.models import (
    StrategyDescriptor, StrategyRole, StrategyProposal, StrategyAction,
    ProposalClass
)
from omega_strategy.eligibility.world_model import eligibility_reasons
from omega_strategy.strategies.common import wait_proposal, neutral_score

class CNYRUBFBRMStrategy:
    descriptor = StrategyDescriptor(
        strategy_id="CNYRUBF_BRM_V100",
        name_ru="CNYRUBF BRM v100",
        instrument_id="CNYRUBF",
        role=StrategyRole.CHAMPION,
        family="CNYRUBF_BRM",
        version="100",
        live_permission=False,
        independent_family="CNY_BRM",
    )

    def evaluate(self, world_model, context):
        reasons = eligibility_reasons(world_model, family=self.descriptor.family)
        if reasons:
            return wait_proposal(self.descriptor, world_model, context, reasons)

        if context.daily_ideas_used_instrument >= 2:
            return wait_proposal(self.descriptor, world_model, context, ["STRAT_IDEA_LIMIT_REACHED"])

        t15 = world_model.timeframes.get("15m")
        t5 = world_model.timeframes.get("5m")
        t1 = world_model.timeframes.get("1m")
        if not (t15 and t5 and t1):
            return wait_proposal(self.descriptor, world_model, context, ["STRAT_EXECUTION_NOT_READY"])

        support = t5.support or t1.support
        resistance = t5.resistance or t1.resistance
        if support is None or resistance is None:
            return wait_proposal(self.descriptor, world_model, context, ["BRAIN_LEVELS_AMBIGUOUS"])

        # Trend filter: metadata may signal a one-way move ~1% without retest.
        move_pct = Decimal(str(world_model.metadata.get("session_directional_move_pct","0")))
        retest_ok = bool(world_model.metadata.get("retest_confirmed", False))
        if abs(move_pct) >= Decimal("0.01") and not retest_ok:
            # Countertrend is blocked; trend-aligned setup may still be considered.
            if move_pct > 0 and world_model.strategic_bias == "SHORT":
                return wait_proposal(self.descriptor, world_model, context, ["STRAT_CNY_TREND_FILTER"])
            if move_pct < 0 and world_model.strategic_bias == "LONG":
                return wait_proposal(self.descriptor, world_model, context, ["STRAT_CNY_TREND_FILTER"])

        price = world_model.price
        atr5 = t5.atr or Decimal("0.01")
        buffer = atr5 * Decimal("0.05")
        quality = min(t15.data_quality_score,t5.data_quality_score,t1.data_quality_score)
        uncertainty = world_model.uncertainty.score

        if world_model.strategic_bias == "LONG":
            entry = support.price + buffer
            stop = support.price - atr5 * Decimal("0.40")
            tp = resistance.price - buffer
            risk = max(entry-stop,Decimal("0.0001"))
            reward = max(tp-entry,Decimal("0"))
            rr = reward/risk
            if rr < Decimal("1.5"):
                return wait_proposal(self.descriptor, world_model, context, ["STRAT_RR_TOO_LOW"])
            return StrategyProposal(
                uuid4(),self.descriptor.strategy_id,"CNYRUBF",context.now,
                StrategyAction.LONG_PROPOSAL,ProposalClass.ENTRY,"BUY",
                entry,stop,tp,Decimal("1"),entry,risk,Decimal("0.75"),
                neutral_score(setup=0.8,regime=0.8,tf=0.9,of=0.6,level=0.9,ctx=0.6,hist=0.5,
                              exec_ready=1,quality=float(quality),uncertainty=float(uncertainty)),
                (),getattr(world_model,"metadata",{}).get("world_model_id","wm"),
                context.now+timedelta(seconds=15),
                {"rr":str(rr),"stack":"15m->5m->1m","no_averaging":True}
            )

        if world_model.strategic_bias == "SHORT":
            entry = resistance.price - buffer
            stop = resistance.price + atr5 * Decimal("0.40")
            tp = support.price + buffer
            risk = max(stop-entry,Decimal("0.0001"))
            reward = max(entry-tp,Decimal("0"))
            rr = reward/risk
            if rr < Decimal("1.5"):
                return wait_proposal(self.descriptor, world_model, context, ["STRAT_RR_TOO_LOW"])
            return StrategyProposal(
                uuid4(),self.descriptor.strategy_id,"CNYRUBF",context.now,
                StrategyAction.SHORT_PROPOSAL,ProposalClass.ENTRY,"SELL",
                entry,stop,tp,Decimal("1"),entry,risk,Decimal("0.75"),
                neutral_score(setup=0.8,regime=0.8,tf=0.9,of=0.6,level=0.9,ctx=0.6,hist=0.5,
                              exec_ready=1,quality=float(quality),uncertainty=float(uncertainty)),
                (),getattr(world_model,"metadata",{}).get("world_model_id","wm"),
                context.now+timedelta(seconds=15),
                {"rr":str(rr),"stack":"15m->5m->1m","no_averaging":True}
            )

        return wait_proposal(self.descriptor, world_model, context, ["STRAT_WAIT"])
