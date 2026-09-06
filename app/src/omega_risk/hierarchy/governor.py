from __future__ import annotations
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from omega_risk.domain.models import (
    RiskRequest, RiskContext, RiskLimits, RiskDecision,
    RiskDecisionStatus, CrisisMode
)
from omega_risk.limits.loss_controls import check_daily_loss, check_drawdown
from omega_risk.limits.exposure import would_exceed, concentration_exceeded
from omega_risk.data_quality.gates import data_quality_reasons
from omega_risk.crisis.modes import risk_multiplier, mode_blocks_new_entries, mode_reason
from omega_risk.audit.policy_hash import make_policy_hash

class RiskGovernor:
    def __init__(self, limits: RiskLimits, *, authorization_ttl_seconds: int = 10) -> None:
        self.limits = limits
        self.authorization_ttl_seconds = authorization_ttl_seconds

    def decide(self, request: RiskRequest, ctx: RiskContext) -> RiskDecision:
        reasons: list[str] = []
        now = datetime.now(timezone.utc)
        policy_hash = make_policy_hash(self.limits)

        if request.requested_risk_rub <= 0 or request.requested_capital_rub <= 0:
            reasons.append("RISK_REQUEST_INVALID")

        if ctx.kill_switch:
            reasons.append("RISK_KILL_SWITCH_ACTIVE")

        crisis_reason = mode_reason(ctx.crisis_mode)
        if crisis_reason:
            reasons.append(crisis_reason)

        reasons.extend(data_quality_reasons(
            market_data_age_seconds=ctx.market_data_age_seconds,
            broker_state_age_seconds=ctx.broker_state_age_seconds,
            data_quality_score=ctx.data_quality_score,
            max_market_data_age_seconds=self.limits.max_market_data_age_seconds,
            max_broker_state_age_seconds=self.limits.max_broker_state_age_seconds,
            min_data_quality_score=self.limits.min_data_quality_score,
            reconciliation_status=ctx.reconciliation_status,
        ))

        if check_daily_loss(ctx.realized_pnl_rub, ctx.unrealized_pnl_rub, self.limits.daily_loss_limit_rub):
            reasons.append("RISK_DAILY_LOSS_LIMIT")

        if check_drawdown(ctx.portfolio_equity_rub, ctx.portfolio_high_water_rub, self.limits.hard_drawdown_limit_rub):
            reasons.append("RISK_DRAWDOWN_LIMIT")

        if ctx.consecutive_losses >= self.limits.max_consecutive_losses_before_safe:
            reasons.append("RISK_CONSECUTIVE_LOSSES_SAFE")
        elif ctx.consecutive_losses >= self.limits.max_consecutive_losses_before_caution:
            reasons.append("RISK_CONSECUTIVE_LOSSES_CAUTION")

        if would_exceed(ctx.strategy_open_risk_rub, request.requested_risk_rub, self.limits.strategy_open_risk_limit_rub):
            reasons.append("RISK_STRATEGY_LIMIT")

        if would_exceed(ctx.account_open_risk_rub, request.requested_risk_rub, self.limits.account_open_risk_limit_rub):
            reasons.append("RISK_ACCOUNT_LIMIT")

        if would_exceed(ctx.portfolio_open_risk_rub, request.requested_risk_rub, self.limits.portfolio_open_risk_limit_rub):
            reasons.append("RISK_PORTFOLIO_LIMIT")

        if concentration_exceeded(
            ctx.instrument_exposure_rub,
            request.requested_capital_rub,
            ctx.portfolio_equity_rub,
            self.limits.max_instrument_concentration_pct,
        ):
            reasons.append("RISK_INSTRUMENT_CONCENTRATION")

        if request.instrument_id == "ROSN" and request.requested_borrowed_increment_rub > 0:
            if request.account_role == "ROSN_HEDGE" or request.side.upper() == "SELL":
                if ctx.current_borrowed_hedge_rub + request.requested_borrowed_increment_rub > self.limits.rosn_borrowed_hedge_limit_rub:
                    reasons.append("RISK_ROSN_BORROWED_HEDGE_LIMIT")
            else:
                if ctx.current_borrowed_long_rub + request.requested_borrowed_increment_rub > self.limits.rosn_borrowed_long_limit_rub:
                    reasons.append("RISK_ROSN_BORROWED_LONG_LIMIT")

        if request.instrument_id == "CNYRUBF" and request.account_role != "CNYRUBF_DEDICATED":
            reasons.append("RISK_CNY_WRONG_ACCOUNT")

        hard_prefixes = (
            "RISK_REQUEST_INVALID",
            "RISK_KILL_SWITCH_ACTIVE",
            "RISK_CRISIS_SAFE",
            "RISK_CRISIS_EMERGENCY",
            "RISK_STALE_",
            "RISK_DATA_QUALITY_LOW",
            "RISK_RECONCILIATION_BLOCK",
            "RISK_DAILY_LOSS_LIMIT",
            "RISK_DRAWDOWN_LIMIT",
            "RISK_CONSECUTIVE_LOSSES_SAFE",
            "RISK_STRATEGY_LIMIT",
            "RISK_ACCOUNT_LIMIT",
            "RISK_PORTFOLIO_LIMIT",
            "RISK_INSTRUMENT_CONCENTRATION",
            "RISK_ROSN_BORROWED_",
            "RISK_CNY_WRONG_ACCOUNT",
        )
        hard = [r for r in reasons if r.startswith(hard_prefixes)]

        if hard:
            return RiskDecision(
                request.request_id,
                RiskDecisionStatus.DENIED,
                Decimal("0"),
                Decimal("0"),
                tuple(sorted(set(reasons))),
                policy_hash,
                now + timedelta(seconds=self.authorization_ttl_seconds),
            )

        multiplier = risk_multiplier(ctx.crisis_mode)
        approved_risk = (request.requested_risk_rub * multiplier).quantize(Decimal("0.01"))
        approved_capital = (request.requested_capital_rub * multiplier).quantize(Decimal("0.01"))

        # A loss-streak warning never increases risk; in CAUTION already multiplier applies.
        if ctx.consecutive_losses >= self.limits.max_consecutive_losses_before_caution and ctx.crisis_mode is CrisisMode.NORMAL:
            approved_risk = (approved_risk * Decimal("0.60")).quantize(Decimal("0.01"))
            approved_capital = (approved_capital * Decimal("0.60")).quantize(Decimal("0.01"))
            reasons.append("RISK_REDUCED_BY_CRISIS_MULTIPLIER")

        if multiplier < Decimal("1.00") and not mode_blocks_new_entries(ctx.crisis_mode):
            reasons.append("RISK_REDUCED_BY_CRISIS_MULTIPLIER")

        # Compare at the same RUB precision used for approvals. A pure kopeck
        # normalization must not create a false REDUCED decision (important for
        # small CNYRUBF sandbox risks such as 0.009 RUB proxies).
        requested_risk_q = request.requested_risk_rub.quantize(Decimal("0.01"))
        requested_capital_q = request.requested_capital_rub.quantize(Decimal("0.01"))
        status = RiskDecisionStatus.APPROVED
        if approved_risk < requested_risk_q or approved_capital < requested_capital_q:
            status = RiskDecisionStatus.REDUCED

        return RiskDecision(
            request.request_id,
            status,
            approved_risk,
            approved_capital,
            tuple(sorted(set(reasons))),
            policy_hash,
            now + timedelta(seconds=self.authorization_ttl_seconds),
        )
