from __future__ import annotations
from omega_data.domain.models import DataClass

DELETE_PRIORITY = {
    DataClass.TEMPORARY: 10,
    DataClass.RESEARCH_INTERMEDIATE: 20,
    DataClass.RESEARCH_RESULT: 30,
    DataClass.MARKET_RAW: 40,
    DataClass.MARKET_AGGREGATED: 50,
    DataClass.BLACKBOX_NORMAL: 60,
    DataClass.BLACKBOX_CRITICAL: 90,
    DataClass.CRITICAL_FINANCIAL: 100,
}

def delete_priority(data_class: DataClass) -> int:
    return DELETE_PRIORITY[data_class]

def can_auto_delete(data_class: DataClass) -> bool:
    return data_class is not DataClass.CRITICAL_FINANCIAL
