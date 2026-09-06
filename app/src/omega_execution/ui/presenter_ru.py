REASONS_RU = {
    "EXEC_UNKNOWN_OUTCOME": "Неизвестно, принял ли брокер заявку. Повторная отправка временно запрещена.",
    "EXEC_SAFE_RETRY_ALLOWED": "Сверка подтвердила отсутствие первоначальной заявки. Безопасный повтор разрешён.",
    "EXEC_POSITION_MISMATCH": "Позиция у брокера не совпадает с локальным состоянием.",
    "EXEC_UNEXPECTED_BROKER_ORDER": "У брокера обнаружена неизвестная системе активная заявка.",
    "EXEC_PARTIAL_FILL": "Заявка исполнена частично.",
    "EXEC_APPROVAL_EXPIRED": "Разрешение на сделку устарело.",
}

def explain_reason_ru(code: str) -> str:
    return REASONS_RU.get(code, f"Техническая причина: {code}")
