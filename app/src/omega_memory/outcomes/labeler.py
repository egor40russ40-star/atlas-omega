from __future__ import annotations
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Iterable
from uuid import uuid4
from omega_memory.domain.models import (
    MarketObservation, PricePoint, HorizonOutcome, ObservationOutcome
)

def _outcome_for_horizon(
    observation: MarketObservation,
    points: list[PricePoint],
    horizon_seconds: int,
) -> HorizonOutcome:
    start_price = Decimal(str(observation.metadata.get("price", "0")))
    if start_price <= 0:
        return HorizonOutcome(
            horizon_seconds,start_price,None,None,None,None,
            None,None,None,None,False
        )

    end_time = observation.observed_at + timedelta(seconds=horizon_seconds)
    eligible = [p for p in points if observation.observed_at < p.occurred_at <= end_time]
    if not eligible:
        return HorizonOutcome(
            horizon_seconds,start_price,None,None,None,None,
            None,None,None,None,False
        )

    eligible.sort(key=lambda x: x.occurred_at)
    last = eligible[-1]
    complete = last.occurred_at >= end_time
    high = max(p.high for p in eligible)
    low = min(p.low for p in eligible)
    end_price = last.price
    ret = (end_price - start_price) / start_price
    mfe_long = (high - start_price) / start_price
    mae_long = (start_price - low) / start_price
    mfe_short = (start_price - low) / start_price
    mae_short = (high - start_price) / start_price

    return HorizonOutcome(
        horizon_seconds,start_price,end_price,ret,high,low,
        mfe_long,mae_long,mfe_short,mae_short,complete
    )

def label_outcomes(
    observation: MarketObservation,
    points: Iterable[PricePoint],
    *,
    horizons_seconds=(60,300,900,1800,3600),
    labeled_at: datetime,
) -> ObservationOutcome:
    pts = list(points)
    horizons = {
        int(h): _outcome_for_horizon(observation,pts,int(h))
        for h in horizons_seconds
    }
    return ObservationOutcome(
        uuid4(),observation.observation_id,labeled_at,
        horizons,observation.source_mode,
        {"labeler":"outcome_v1"}
    )
