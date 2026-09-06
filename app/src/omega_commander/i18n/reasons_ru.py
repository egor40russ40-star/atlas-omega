REASONS_RU = {
    "CMD_AUTH_REQUIRED":"Требуется авторизация.",
    "CMD_ROLE_DENIED":"Недостаточно прав.",
    "CMD_PERMANENTLY_FORBIDDEN":"Команда запрещена архитектурой безопасности.",
    "CMD_CONFIRMATION_REQUIRED":"Требуется отдельное подтверждение.",
    "CMD_CONFIRMATION_EXPIRED":"Подтверждение истекло.",
    "CMD_CONFIRMATION_HASH_MISMATCH":"Параметры команды изменились после подтверждения.",
    "CMD_SAFE_PAUSE_ACTIVE":"Безопасная пауза активна.",
    "CMD_ENTERED_SAFE":"Система переведена в SAFE.",
    "CMD_EMERGENCY_STOP_ACTIVE":"Аварийная остановка активна.",
    "CMD_RESUME_DENIED_NOT_READY":"Система ещё не READY.",
    "CMD_RESUME_DENIED_KILL_SWITCH":"Kill Switch активен.",
    "CMD_CRITICAL_RESTART_REQUIRES_SAFE":"Критический сервис можно перезапускать только в SAFE/RECOVERY.",
}

def reason_ru(code: str) -> str:
    return REASONS_RU.get(code,f"Техническая причина: {code}")
