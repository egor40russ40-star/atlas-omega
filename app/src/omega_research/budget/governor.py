from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class ResearchUsage:
    running_jobs: int
    daily_cpu_minutes: Decimal
    daily_output_gb: Decimal
    candidates_today: int
    experiments_today: int

@dataclass(frozen=True, slots=True)
class ResearchBudget:
    max_running_jobs: int
    max_daily_cpu_minutes: Decimal
    max_daily_output_gb: Decimal
    max_candidates_per_family_per_day: int
    max_experiments_per_day: int

def budget_reasons(usage: ResearchUsage, budget: ResearchBudget) -> list[str]:
    reasons=[]
    if usage.running_jobs >= budget.max_running_jobs:
        reasons.append("RESEARCH_BUDGET_EXCEEDED")
    if usage.daily_cpu_minutes >= budget.max_daily_cpu_minutes:
        reasons.append("RESEARCH_BUDGET_EXCEEDED")
    if usage.daily_output_gb >= budget.max_daily_output_gb:
        reasons.append("RESEARCH_BUDGET_EXCEEDED")
    if usage.candidates_today >= budget.max_candidates_per_family_per_day:
        reasons.append("RESEARCH_BUDGET_EXCEEDED")
    if usage.experiments_today >= budget.max_experiments_per_day:
        reasons.append("RESEARCH_BUDGET_EXCEEDED")
    return sorted(set(reasons))
