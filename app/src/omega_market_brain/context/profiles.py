ROSN_CONTEXT_NODES = (
    "IMOEX",
    "OIL_SECTOR",
    "OIL",
    "RUB",
    "ROSN_NEWS",
    "SANCTIONS_REGULATION",
    "MARKET_LIQUIDITY",
    "RISK_ON_OFF",
)

CNYRUBF_CONTEXT_NODES = (
    "CNY_RUB_REFERENCE",
    "RUB_STATE",
    "CNY_STATE",
    "FX_REGIME",
    "RATES_MACRO",
    "LIQUIDITY_SPREAD",
    "SESSION_TIME",
    "EVENT_RISK",
)

def expected_nodes(instrument_id: str) -> tuple[str, ...]:
    if instrument_id == "ROSN":
        return ROSN_CONTEXT_NODES
    if instrument_id == "CNYRUBF":
        return CNYRUBF_CONTEXT_NODES
    return ()
