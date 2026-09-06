from __future__ import annotations
from decimal import Decimal

def trading_equity(
    broker_equity: Decimal,
    cumulative_external_deposits: Decimal,
    cumulative_external_withdrawals: Decimal,
) -> Decimal:
    net_external_flow = cumulative_external_deposits - cumulative_external_withdrawals
    return broker_equity - net_external_flow

def net_external_flow(deposits: Decimal, withdrawals: Decimal) -> Decimal:
    return deposits - withdrawals
