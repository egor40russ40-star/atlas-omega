from __future__ import annotations
from decimal import Decimal
from uuid import uuid4
from omega_memory.domain.models import (
    MarketObservation, ObservationOutcome, WaitEvaluation, WaitOutcomeClass
)

def evaluate_wait(
    observation: MarketObservation,
    outcome: ObservationOutcome,
    *,
    horizon_seconds: int = 900,
    good_mfe_pct: Decimal = Decimal("0.005"),
    bad_mae_pct: Decimal = Decimal("0.005"),
) -> WaitEvaluation:
    h = outcome.horizons.get(horizon_seconds)
    direction = observation.strategic_bias if observation.strategic_bias in {"LONG","SHORT"} else None

    if h is None or not h.path_complete:
        return WaitEvaluation(
            uuid4(),observation.observation_id,observation.selected_strategy_id,
            observation.wait_reason_codes,direction,WaitOutcomeClass.INCOMPLETE,
            horizon_seconds,None,{"reason":"MEMORY_OUTCOME_INCOMPLETE"}
        )

    if direction is None:
        return WaitEvaluation(
            uuid4(),observation.observation_id,observation.selected_strategy_id,
            observation.wait_reason_codes,None,WaitOutcomeClass.UNEVALUABLE,
            horizon_seconds,None,{}
        )

    if direction == "LONG":
        mfe = h.mfe_long_pct or Decimal("0")
        mae = h.mae_long_pct or Decimal("0")
    else:
        mfe = h.mfe_short_pct or Decimal("0")
        mae = h.mae_short_pct or Decimal("0")

    if mae >= bad_mae_pct and mfe < good_mfe_pct:
        cls = WaitOutcomeClass.AVOIDED_BAD
        utility = mae / bad_mae_pct if bad_mae_pct > 0 else Decimal("1")
    elif mfe >= good_mfe_pct and mae < bad_mae_pct:
        cls = WaitOutcomeClass.MISSED_GOOD
        utility = -(mfe / good_mfe_pct if good_mfe_pct > 0 else Decimal("1"))
    else:
        cls = WaitOutcomeClass.NEUTRAL
        utility = Decimal("0")

    return WaitEvaluation(
        uuid4(),observation.observation_id,observation.selected_strategy_id,
        observation.wait_reason_codes,direction,cls,horizon_seconds,utility,
        {"mfe_pct":str(mfe),"mae_pct":str(mae)}
    )
