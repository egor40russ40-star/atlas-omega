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

class ROSNCoreStrategy:
    descriptor = StrategyDescriptor(
        strategy_id="ROSN_CORE_V100",
        name_ru="ROSN Core v100",
        instrument_id="ROSN",
        role=StrategyRole.CHAMPION,
        family="ROSN_CORE",
        version="100",
        live_permission=False,
        sandbox_only=False,
        independent_family="ROSN_STRUCTURAL",
    )

    def evaluate(self, world_model, context):
        reasons = eligibility_reasons(world_model, family=self.descriptor.family)
        if reasons:
            return wait_proposal(self.descriptor, world_model, context, reasons)

        tf = world_model.timeframes
        one = tf.get("1m")
        five = tf.get("5m")
        if one is None or five is None:
            return wait_proposal(self.descriptor, world_model, context, ["STRAT_EXECUTION_NOT_READY"])

        # nearest tactical levels
        support = five.support or one.support
        resistance = five.resistance or one.resistance
        price = world_model.price
        if support is None or resistance is None:
            return wait_proposal(self.descriptor, world_model, context, ["BRAIN_LEVELS_AMBIGUOUS"])

        uncertainty = world_model.uncertainty.score
        quality = min(one.data_quality_score, five.data_quality_score)
        of_support = Decimal("0.5")
        if world_model.orderflow is not None:
            of_support = (world_model.orderflow.pressure_score + Decimal("1")) / Decimal("2")

        # Keep entry "before" support/resistance rather than exactly on it.
        buffer = (five.atr or Decimal("1")) * Decimal("0.05")
        if world_model.strategic_bias == "LONG":
            entry = support.price + buffer
            if price < support.price or price > resistance.price:
                return wait_proposal(self.descriptor, world_model, context, ["STRAT_WAIT"])
            stop = support.price - (five.atr or Decimal("1")) * Decimal("0.35")
            tp = resistance.price - buffer
            risk_per_unit = max(entry - stop, Decimal("0.01"))
            reward = max(tp - entry, Decimal("0"))
            rr = reward / risk_per_unit
            if rr < Decimal("1.5"):
                return wait_proposal(self.descriptor, world_model, context, ["STRAT_RR_TOO_LOW"])
            return StrategyProposal(
                uuid4(), self.descriptor.strategy_id, "ROSN", context.now,
                StrategyAction.LONG_PROPOSAL, ProposalClass.ENTRY, "BUY",
                entry, stop, tp, Decimal("1"),
                entry, risk_per_unit, Decimal("0.75"),
                neutral_score(
                    setup=0.8, regime=0.8, tf=0.8, of=float(of_support),
                    level=0.9, ctx=0.7, hist=0.5, exec_ready=1,
                    quality=float(quality), uncertainty=float(uncertainty)
                ),
                (), getattr(world_model,"metadata",{}).get("world_model_id","wm"),
                context.now + timedelta(seconds=20),
                {"rr": str(rr), "rule":"LONG_BEFORE_SUPPORT_TP_BEFORE_RESISTANCE"}
            )

        if world_model.strategic_bias == "SHORT":
            entry = resistance.price - buffer
            if price < support.price or price > resistance.price:
                return wait_proposal(self.descriptor, world_model, context, ["STRAT_WAIT"])
            stop = resistance.price + (five.atr or Decimal("1")) * Decimal("0.35")
            tp = support.price + buffer
            risk_per_unit = max(stop - entry, Decimal("0.01"))
            reward = max(entry - tp, Decimal("0"))
            rr = reward / risk_per_unit
            if rr < Decimal("1.5"):
                return wait_proposal(self.descriptor, world_model, context, ["STRAT_RR_TOO_LOW"])
            return StrategyProposal(
                uuid4(), self.descriptor.strategy_id, "ROSN", context.now,
                StrategyAction.SHORT_PROPOSAL, ProposalClass.ENTRY, "SELL",
                entry, stop, tp, Decimal("1"),
                entry, risk_per_unit, Decimal("0.75"),
                neutral_score(
                    setup=0.8, regime=0.8, tf=0.8, of=float(1-of_support),
                    level=0.9, ctx=0.7, hist=0.5, exec_ready=1,
                    quality=float(quality), uncertainty=float(uncertainty)
                ),
                (), getattr(world_model,"metadata",{}).get("world_model_id","wm"),
                context.now + timedelta(seconds=20),
                {"rr": str(rr), "rule":"SHORT_BEFORE_RESISTANCE_TP_BEFORE_SUPPORT"}
            )

        return wait_proposal(self.descriptor, world_model, context, ["STRAT_WAIT"])
