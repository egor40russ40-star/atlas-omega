from __future__ import annotations
from decimal import Decimal
from uuid import uuid4, UUID
from omega_memory.domain.models import CounterfactualScenario, CounterfactualType

def entry_offset_scenario(
    *,
    parent_observation_id: UUID,
    side: str,
    base_entry: Decimal,
    offset: Decimal,
    stop_price: Decimal | None,
    take_profit_price: Decimal | None,
    version: str = "cf-v1",
) -> CounterfactualScenario:
    entry=base_entry+offset if side=="BUY" else base_entry-offset
    return CounterfactualScenario(
        uuid4(),parent_observation_id,CounterfactualType.ENTRY_OFFSET,
        version,side,entry,stop_price,take_profit_price,
        {"offset":str(offset)}
    )

def stop_multiplier_scenario(
    *,
    parent_observation_id: UUID,
    side: str,
    entry_price: Decimal,
    base_stop_price: Decimal,
    take_profit_price: Decimal | None,
    multiplier: Decimal,
    version: str = "cf-v1",
) -> CounterfactualScenario:
    distance=abs(entry_price-base_stop_price)*multiplier
    stop=entry_price-distance if side=="BUY" else entry_price+distance
    return CounterfactualScenario(
        uuid4(),parent_observation_id,CounterfactualType.STOP_MULTIPLIER,
        version,side,entry_price,stop,take_profit_price,
        {"multiplier":str(multiplier)}
    )
