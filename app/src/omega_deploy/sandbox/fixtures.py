from __future__ import annotations
from types import SimpleNamespace
from datetime import datetime,timezone
from decimal import Decimal
from uuid import uuid4

from omega_treasury.types import AccountRecord,AccountRole,AccountState
from omega_treasury.capital.pool import CapitalPool
from omega_risk.domain.models import RiskContext,RiskLimits,CrisisMode
from omega_execution.domain.models import InstrumentRules

def tf(score=Decimal("0.7"), support="100", resistance="110", atr="2"):
    return SimpleNamespace(
        support=SimpleNamespace(price=Decimal(support),strength=Decimal("0.8")),
        resistance=SimpleNamespace(price=Decimal(resistance),strength=Decimal("0.8")),
        atr=Decimal(atr),data_quality_score=Decimal("1"),confidence=Decimal("0.9"),
        direction_score=score,atr_pct=Decimal("0.02"),volume_ratio=Decimal("1.1")
    )

def world(instrument_id: str,bias: str="LONG"):
    if instrument_id=="CNYRUBF":
        support,resistance,price,atr="12.80","12.90","12.84","0.02"
    else:
        support,resistance,price,atr="300","320","310","5"
    t=tf(Decimal("0.7") if bias=="LONG" else Decimal("-0.7"),support,resistance,atr)
    return SimpleNamespace(
        instrument_id=instrument_id,
        dominant_regime="TREND_UP" if bias=="LONG" else "TREND_DOWN",
        execution_ready=True,no_trade=False,strategic_bias=bias,
        price=Decimal(price),
        uncertainty=SimpleNamespace(score=Decimal("0.1")),
        orderflow=SimpleNamespace(pressure_score=Decimal("0.5") if bias=="LONG" else Decimal("-0.5")),
        timeframes={"1m":t,"5m":t,"15m":t,"1h":t,"4h":t,"1D":t},
        metadata={"world_model_id":f"wm-sandbox-{instrument_id}",
                  "retest_confirmed":True,"session_directional_move_pct":"0"}
    )

def account_and_pool(instrument_id: str,strategy_id: str):
    if instrument_id=="CNYRUBF":
        role=AccountRole.CNYRUBF_DEDICATED
        name="CNYRUBF Sandbox"
        allowed=(instrument_id,)
    else:
        role=AccountRole.ROSN_PRIMARY
        name="ROSN Sandbox"
        allowed=(instrument_id,)
    a=AccountRecord(
        uuid4(),f"FAKE-{instrument_id}-ACCOUNT",name,role,AccountState.ENABLED,
        (strategy_id,),allowed
    )
    p=CapitalPool(uuid4(),a.internal_account_id,strategy_id,"RUB",
                  allocated=Decimal("10000"),safety_reserve=Decimal("1000"))
    return a,p

def risk_context(*,borrowed_long="0",borrowed_hedge="0",kill_switch=False,data_age="0.1",broker_age="0.1"):
    return RiskContext(
        realized_pnl_rub=Decimal("0"),unrealized_pnl_rub=Decimal("0"),
        portfolio_equity_rub=Decimal("10000"),portfolio_high_water_rub=Decimal("10000"),
        strategy_open_risk_rub=Decimal("0"),account_open_risk_rub=Decimal("0"),
        portfolio_open_risk_rub=Decimal("0"),instrument_exposure_rub=Decimal("0"),
        current_borrowed_long_rub=Decimal(borrowed_long),
        current_borrowed_hedge_rub=Decimal(borrowed_hedge),
        consecutive_losses=0,market_data_age_seconds=Decimal(data_age),
        broker_state_age_seconds=Decimal(broker_age),data_quality_score=Decimal("1"),
        reconciliation_status="OK",crisis_mode=CrisisMode.NORMAL,kill_switch=kill_switch,
    )

def risk_limits():
    return RiskLimits(
        daily_loss_limit_rub=Decimal("300"),
        strategy_open_risk_limit_rub=Decimal("500"),
        account_open_risk_limit_rub=Decimal("1000"),
        portfolio_open_risk_limit_rub=Decimal("2000"),
    )

def instrument_rules(instrument_id: str):
    if instrument_id=="CNYRUBF":
        return InstrumentRules(instrument_id,Decimal("1"),Decimal("1"),Decimal("0.001"),Decimal("1"))
    return InstrumentRules(instrument_id,Decimal("1"),Decimal("1"),Decimal("0.01"),Decimal("1"))
