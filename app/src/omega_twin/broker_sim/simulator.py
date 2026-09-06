from __future__ import annotations
from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from typing import MutableMapping

from omega_twin.domain.models import SimOrder, SimOrderState, SimFill, MarketBar
from omega_twin.costs.model import CostModel
from omega_twin.slippage.model import SlippageModel
from omega_twin.fills.liquidity import FillLiquidityModel

class BrokerSimulator:
    def __init__(
        self,
        *,
        cost_model: CostModel,
        slippage_model: SlippageModel,
        liquidity_model: FillLiquidityModel,
        bar_path_policy: str = "ADVERSE_FIRST",
    ) -> None:
        self.cost_model = cost_model
        self.slippage_model = slippage_model
        self.liquidity_model = liquidity_model
        self.bar_path_policy = bar_path_policy
        self.orders: MutableMapping[str, SimOrder] = {}
        self.fills: list[SimFill] = []

    def submit(
        self,
        *,
        client_id: str,
        instrument_id: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        created_at: datetime,
        limit_price: Decimal | None = None,
        stop_price: Decimal | None = None,
    ) -> SimOrder:
        if client_id in self.orders:
            return self.orders[client_id]
        if quantity <= 0:
            order = SimOrder(
                uuid4(),client_id,instrument_id,side,order_type,quantity,quantity,
                SimOrderState.REJECTED,created_at,limit_price,stop_price
            )
            self.orders[client_id]=order
            return order
        order = SimOrder(
            uuid4(),client_id,instrument_id,side,order_type,quantity,quantity,
            SimOrderState.ACCEPTED,created_at,limit_price,stop_price
        )
        self.orders[client_id]=order
        return order

    def cancel(self, client_id: str) -> SimOrder:
        order = self.orders[client_id]
        if order.state in {SimOrderState.FILLED,SimOrderState.CANCELLED,SimOrderState.REJECTED,SimOrderState.EXPIRED}:
            return order
        updated = replace(order,state=SimOrderState.CANCELLED)
        self.orders[client_id]=updated
        return updated

    def _trigger_price(self, order: SimOrder, bar: MarketBar) -> Decimal | None:
        t = order.order_type.upper()
        if t == "MARKET":
            return bar.open
        if t == "LIMIT":
            if order.side=="BUY" and order.limit_price is not None and bar.low <= order.limit_price:
                return order.limit_price
            if order.side=="SELL" and order.limit_price is not None and bar.high >= order.limit_price:
                return order.limit_price
            return None
        if t == "STOP":
            if order.side=="BUY" and order.stop_price is not None and bar.high >= order.stop_price:
                return max(order.stop_price, bar.open)
            if order.side=="SELL" and order.stop_price is not None and bar.low <= order.stop_price:
                return min(order.stop_price, bar.open)
            return None
        if t == "STOP_LIMIT":
            if order.stop_price is None or order.limit_price is None:
                return None
            triggered = (
                (order.side=="BUY" and bar.high >= order.stop_price)
                or (order.side=="SELL" and bar.low <= order.stop_price)
            )
            if not triggered:
                return None
            if order.side=="BUY" and bar.low <= order.limit_price:
                return order.limit_price
            if order.side=="SELL" and bar.high >= order.limit_price:
                return order.limit_price
            return None
        return None

    def process_bar(
        self,
        client_id: str,
        bar: MarketBar,
        *,
        volatility_score: Decimal = Decimal("0"),
        liquidity_penalty: Decimal = Decimal("0"),
    ) -> tuple[SimOrder, tuple[SimFill,...]]:
        order = self.orders[client_id]
        if order.state not in {SimOrderState.ACCEPTED,SimOrderState.PARTIALLY_FILLED}:
            return order, ()

        trigger = self._trigger_price(order,bar)
        if trigger is None:
            return order, ()

        qty = self.liquidity_model.fillable_quantity(
            requested_remaining=order.remaining_quantity,
            bar_volume=bar.volume,
        )
        if qty <= 0:
            return order, ()

        fill_price, slip_per_unit = self.slippage_model.apply(
            trigger,side=order.side,
            volatility_score=volatility_score,
            liquidity_penalty=liquidity_penalty,
        )
        notional = fill_price * qty
        commission = self.cost_model.commission(notional)
        fill = SimFill(
            uuid4(),order.order_id,bar.closed_at,qty,fill_price,
            commission,slip_per_unit*qty
        )
        self.fills.append(fill)

        new_filled = order.filled_quantity + qty
        new_remaining = max(order.quantity-new_filled,Decimal("0"))
        if order.average_fill_price is None:
            avg = fill_price
        else:
            prev_notional = order.average_fill_price*order.filled_quantity
            avg = (prev_notional+fill_price*qty)/new_filled

        state = SimOrderState.FILLED if new_remaining == 0 else SimOrderState.PARTIALLY_FILLED
        updated = replace(
            order,state=state,filled_quantity=new_filled,
            remaining_quantity=new_remaining,average_fill_price=avg
        )
        self.orders[client_id]=updated
        return updated,(fill,)
