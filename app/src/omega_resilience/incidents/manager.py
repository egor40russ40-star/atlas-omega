from __future__ import annotations
from dataclasses import replace
from datetime import datetime
from uuid import uuid4
from omega_resilience.domain.models import Incident, IncidentSeverity

class IncidentManager:
    def __init__(self):
        self._open_by_fingerprint={}

    def report(
        self,
        *,
        fingerprint: str,
        severity: IncidentSeverity,
        category: str,
        affected_services: tuple[str,...],
        reason_codes: tuple[str,...],
        message_ru: str,
        now: datetime,
    ) -> Incident:
        current=self._open_by_fingerprint.get(fingerprint)
        if current and current.resolved_at is None:
            updated=replace(
                current,
                last_seen_at=now,
                occurrence_count=current.occurrence_count+1,
                reason_codes=tuple(sorted(set(current.reason_codes+reason_codes))),
            )
            self._open_by_fingerprint[fingerprint]=updated
            return updated
        incident=Incident(
            str(uuid4()),fingerprint,severity,category,affected_services,
            now,now,1,reason_codes,message_ru
        )
        self._open_by_fingerprint[fingerprint]=incident
        return incident

    def resolve(self,fingerprint: str,*,now:datetime):
        current=self._open_by_fingerprint[fingerprint]
        updated=replace(current,resolved_at=now,last_seen_at=now)
        self._open_by_fingerprint[fingerprint]=updated
        return updated
