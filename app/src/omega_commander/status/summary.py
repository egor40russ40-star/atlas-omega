from __future__ import annotations

def trading_readiness_ru(status) -> tuple[str,str]:
    if status.kill_switch_active:
        return "АВАРИЙНАЯ БЛОКИРОВКА","Новые торговые действия заблокированы Kill Switch."
    if status.operational_state in {"SAFE","EMERGENCY","RECOVERY"}:
        return "НЕ ГОТОВ","Система находится в защитном/восстановительном режиме."
    if status.safe_pause_active:
        return "ПАУЗА","Новые входы поставлены на безопасную паузу."
    if not status.broker_connected:
        return "НЕ ГОТОВ","Нет подтверждённого соединения с брокером."
    if status.reconciliation_status not in {"OK","WARNING"}:
        return "НЕ ГОТОВ","Сверка заявок/позиций с брокером не завершена."
    if not status.market_data_fresh:
        return "НЕ ГОТОВ","Рыночные данные устарели."
    if status.operational_state == "READY":
        return "ГОТОВ","Все базовые проверки допускают переход к торговому контуру."
    if status.operational_state == "LIVE":
        return "ТОРГОВЛЯ АКТИВНА","LIVE-контур работает."
    return "ОЖИДАНИЕ","Требуется дополнительная проверка состояния."
