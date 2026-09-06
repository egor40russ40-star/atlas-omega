from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable
from omega_execution.domain.models import (
    BrokerSubmitResult,BrokerSubmitStatus,BrokerOrderSnapshot,BrokerPositionSnapshot
)

@dataclass(frozen=True, slots=True)
class FakeBrokerFaultPlan:
    next_submit_status: BrokerSubmitStatus | None = None
    reject_message: str = "FAKE_REJECTED"

class FakeBrokerExecutionPort:
    def __init__(self, fault_plan: FakeBrokerFaultPlan | None=None):
        self.fault_plan=fault_plan or FakeBrokerFaultPlan()
        self.calls=[]
        self._orders_by_tag={}
        self._recent=[]
        self._positions={}

    def submit_order(self,request):
        # Idempotency on client tag / execution idempotency key.
        existing=self._orders_by_tag.get(request.idempotency_key)
        if existing is not None:
            return BrokerSubmitResult(
                BrokerSubmitStatus.ACCEPTED,existing.broker_order_id,"FAKE_IDEMPOTENT_REPLAY"
            )

        self.calls.append(request)
        status=self.fault_plan.next_submit_status or BrokerSubmitStatus.ACCEPTED
        self.fault_plan=FakeBrokerFaultPlan()

        if status is BrokerSubmitStatus.REJECTED:
            return BrokerSubmitResult(status,None,"FAKE_REJECTED")
        if status in {BrokerSubmitStatus.TIMEOUT,BrokerSubmitStatus.CONNECTION_LOST,BrokerSubmitStatus.UNKNOWN}:
            return BrokerSubmitResult(status,None,"FAKE_AMBIGUOUS")

        oid=f"FAKE-{len(self._recent)+1:06d}"
        snap=BrokerOrderSnapshot(
            oid,request.broker_account_id,request.instrument_id,request.side,"ACTIVE",
            request.quantity,Decimal("0"),None,request.idempotency_key
        )
        self._orders_by_tag[request.idempotency_key]=snap
        self._recent.append(snap)
        return BrokerSubmitResult(BrokerSubmitStatus.ACCEPTED,oid,"FAKE_ACCEPTED")

    def cancel_order(self,broker_account_id: str,broker_order_id: str):
        found=None
        for tag,s in list(self._orders_by_tag.items()):
            if s.broker_order_id==broker_order_id and s.broker_account_id==broker_account_id:
                found=s
                cancelled=BrokerOrderSnapshot(
                    s.broker_order_id,s.broker_account_id,s.instrument_id,s.side,"CANCELLED",
                    s.requested_quantity,s.filled_quantity,s.average_fill_price,s.client_tag
                )
                self._orders_by_tag.pop(tag,None)
                self._recent.append(cancelled)
                break
        if found is None:
            return BrokerSubmitResult(BrokerSubmitStatus.REJECTED,None,"FAKE_ORDER_NOT_FOUND")
        return BrokerSubmitResult(BrokerSubmitStatus.ACCEPTED,broker_order_id,"FAKE_CANCELLED")

    def get_active_orders(self,broker_account_id: str) -> Iterable[BrokerOrderSnapshot]:
        return tuple(
            s for s in self._orders_by_tag.values()
            if s.broker_account_id==broker_account_id and s.state=="ACTIVE"
        )

    def get_recent_orders(self,broker_account_id: str) -> Iterable[BrokerOrderSnapshot]:
        return tuple(s for s in self._recent if s.broker_account_id==broker_account_id)

    def get_positions(self,broker_account_id: str) -> Iterable[BrokerPositionSnapshot]:
        return tuple(
            p for (acc,_),p in self._positions.items() if acc==broker_account_id
        )

    def find_order_by_client_tag(self,broker_account_id: str,client_tag: str):
        s=self._orders_by_tag.get(client_tag)
        return s if s and s.broker_account_id==broker_account_id else None

    def set_position(self,broker_account_id: str,instrument_id: str,quantity: Decimal,average_price: Decimal|None=None):
        p=BrokerPositionSnapshot(broker_account_id,instrument_id,quantity,average_price)
        self._positions[(broker_account_id,instrument_id)]=p
        return p
