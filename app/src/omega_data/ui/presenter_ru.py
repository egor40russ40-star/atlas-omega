def storage_status_ru(mode: str, free_gb: float, actions: tuple[str, ...]) -> str:
    labels = {
        "NORMAL":"НОРМА",
        "CAUTION":"ВНИМАНИЕ",
        "DEFENSIVE":"ЗАЩИТНЫЙ РЕЖИМ",
        "CRITICAL":"КРИТИЧЕСКИ МАЛО МЕСТА",
        "EMERGENCY":"АВАРИЙНЫЙ РЕЖИМ ХРАНЕНИЯ",
    }
    lines = [
        f"Хранилище: {labels.get(mode, mode)}",
        f"Свободно: {free_gb:.1f} ГБ",
    ]
    if actions:
        lines.append("Автоматические действия:")
        lines.extend(f"- {a}" for a in actions)
    return "\n".join(lines)
