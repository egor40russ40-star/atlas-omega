def recovery_status_ru(state: str, reasons: tuple[str,...]=()) -> str:
    names={
        "BOOT":"ЗАГРУЗКА",
        "SELF_TEST":"САМОПРОВЕРКА",
        "BROKER_CONNECT":"ПОДКЛЮЧЕНИЕ К БРОКЕРУ",
        "ACCOUNT_SYNC":"СВЕРКА СЧЕТОВ",
        "POSITION_SYNC":"СВЕРКА ПОЗИЦИЙ",
        "ORDER_SYNC":"СВЕРКА ЗАЯВОК",
        "DATABASE_RECONCILIATION":"СВЕРКА БАЗЫ",
        "RISK_REBUILD":"ВОССТАНОВЛЕНИЕ РИСКА",
        "MARKET_DATA_HEALTH":"ПРОВЕРКА РЫНКА",
        "SAFE":"БЕЗОПАСНЫЙ РЕЖИМ",
        "READY":"ГОТОВ",
        "LIVE":"ТОРГОВЛЯ АКТИВНА",
        "RECOVERY":"ВОССТАНОВЛЕНИЕ",
        "EMERGENCY":"АВАРИЙНЫЙ РЕЖИМ",
    }
    lines=[f"Состояние: {names.get(state,state)}"]
    if reasons:
        lines.append("Причины:")
        lines.extend(f"- {x}" for x in reasons)
    return "\n".join(lines)
