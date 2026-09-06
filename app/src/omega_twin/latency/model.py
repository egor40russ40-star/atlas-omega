from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass(frozen=True, slots=True)
class LatencyModel:
    submit_ms: int = 0
    cancel_ms: int = 0
    market_data_ms: int = 0
    version: str = "latency-v1"

    def submission_visible_at(self, created_at: datetime) -> datetime:
        return created_at + timedelta(milliseconds=self.submit_ms)

    def cancellation_effective_at(self, requested_at: datetime) -> datetime:
        return requested_at + timedelta(milliseconds=self.cancel_ms)

    def market_data_available_at(self, occurred_at: datetime) -> datetime:
        return occurred_at + timedelta(milliseconds=self.market_data_ms)
