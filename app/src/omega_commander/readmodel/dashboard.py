from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Any

@dataclass(frozen=True, slots=True)
class DashboardSection:
    key: str
    title_ru: str
    status: str
    summary_ru: str
    details: Mapping[str,Any]

ORDER = (
    "system",
    "market",
    "accounts",
    "positions",
    "orders",
    "strategies",
    "risk",
    "performance",
    "research",
    "computer",
    "incidents",
    "journal",
)

TITLES = {
    "system":"Система",
    "market":"Рынок и сигналы",
    "accounts":"Счета и деньги",
    "positions":"Позиции",
    "orders":"Заявки",
    "strategies":"Стратегии",
    "risk":"Риск и безопасность",
    "performance":"Прибыль и статистика",
    "research":"Исследования",
    "computer":"Компьютер",
    "incidents":"Ошибки и диагностика",
    "journal":"Журнал",
}

def ordered_sections(sections: Mapping[str,DashboardSection]) -> tuple[DashboardSection,...]:
    return tuple(sections[k] for k in ORDER if k in sections)
