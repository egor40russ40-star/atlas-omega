from __future__ import annotations
from decimal import Decimal
from omega_treasury.types import (
    AccountRecord, AccountRole, CapitalRequest, CapitalDecision,
    CapitalDecisionStatus
)
from .pool import CapitalPool

class CapitalGovernor:
    def __init__(
        self,
        *,
        rosn_borrowed_long_limit_rub: Decimal = Decimal("5000"),
        rosn_borrowed_hedge_limit_rub: Decimal = Decimal("5000"),
    ) -> None:
        self.rosn_borrowed_long_limit_rub = rosn_borrowed_long_limit_rub
        self.rosn_borrowed_hedge_limit_rub = rosn_borrowed_hedge_limit_rub

    def decide(
        self,
        request: CapitalRequest,
        account: AccountRecord,
        pool: CapitalPool,
        *,
        current_borrowed_long_rub: Decimal = Decimal("0"),
        current_borrowed_hedge_rub: Decimal = Decimal("0"),
        margin_classification_known: bool = True,
    ) -> CapitalDecision:
        reasons: list[str] = []

        if account.role is AccountRole.CNYRUBF_DEDICATED:
            pass
        elif request.instrument_id == "CNYRUBF":
            return CapitalDecision(
                request.request_id, CapitalDecisionStatus.DENIED,
                Decimal("0"), Decimal("0"), Decimal("0"),
                ("TREASURY_CNY_WRONG_ACCOUNT",)
            )

        if request.requested_borrowed_increment > 0 and not margin_classification_known:
            return CapitalDecision(
                request.request_id, CapitalDecisionStatus.DENIED,
                Decimal("0"), Decimal("0"), Decimal("0"),
                ("TREASURY_MARGIN_CLASSIFICATION_UNKNOWN",)
            )

        if request.instrument_id == "ROSN" and request.requested_borrowed_increment > 0:
            if account.role is AccountRole.ROSN_HEDGE:
                projected = current_borrowed_hedge_rub + request.requested_borrowed_increment
                if projected > self.rosn_borrowed_hedge_limit_rub:
                    return CapitalDecision(
                        request.request_id, CapitalDecisionStatus.DENIED,
                        Decimal("0"), Decimal("0"), Decimal("0"),
                        ("TREASURY_BORROWED_HEDGE_LIMIT",)
                    )
            else:
                projected = current_borrowed_long_rub + request.requested_borrowed_increment
                if projected > self.rosn_borrowed_long_limit_rub:
                    return CapitalDecision(
                        request.request_id, CapitalDecisionStatus.DENIED,
                        Decimal("0"), Decimal("0"), Decimal("0"),
                        ("TREASURY_BORROWED_LONG_LIMIT",)
                    )

        available = pool.available
        if available <= 0:
            return CapitalDecision(
                request.request_id, CapitalDecisionStatus.DENIED,
                Decimal("0"), Decimal("0"), Decimal("0"),
                ("TREASURY_INSUFFICIENT_AVAILABLE_CAPITAL",)
            )

        if request.requested_capital <= available:
            return CapitalDecision(
                request.request_id,
                CapitalDecisionStatus.APPROVED,
                request.requested_capital,
                request.requested_risk,
                request.requested_borrowed_increment,
                ()
            )

        # Conservative reduction: approve only available capital, never negative.
        ratio = (available / request.requested_capital) if request.requested_capital > 0 else Decimal("0")
        approved_risk = (request.requested_risk * ratio).quantize(Decimal("0.01"))
        return CapitalDecision(
            request.request_id,
            CapitalDecisionStatus.REDUCED,
            available,
            approved_risk,
            Decimal("0"),
            ("TREASURY_INSUFFICIENT_AVAILABLE_CAPITAL",)
        )
