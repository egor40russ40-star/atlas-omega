from __future__ import annotations
from dataclasses import replace
from datetime import datetime
from uuid import UUID
from omega_research.domain.models import ResearchJob, JobState

class ResearchQueue:
    def __init__(self) -> None:
        self._jobs: dict[UUID,ResearchJob] = {}

    def add(self, job: ResearchJob) -> None:
        if job.job_id in self._jobs:
            return
        self._jobs[job.job_id]=job

    def next_jobs(self, limit: int) -> tuple[ResearchJob,...]:
        queued=[j for j in self._jobs.values() if j.state is JobState.QUEUED]
        queued.sort(key=lambda x:(-x.priority,x.queued_at,str(x.job_id)))
        return tuple(queued[:limit])

    def start(self, job_id: UUID, *, now: datetime) -> ResearchJob:
        j=self._jobs[job_id]
        if j.state is not JobState.QUEUED:
            raise ValueError("job not queued")
        u=replace(j,state=JobState.RUNNING,started_at=now)
        self._jobs[job_id]=u
        return u

    def pause(self, job_id: UUID, reason_code: str) -> ResearchJob:
        j=self._jobs[job_id]
        if j.state is not JobState.RUNNING:
            return j
        u=replace(j,state=JobState.PAUSED,reason_codes=tuple(sorted(set(j.reason_codes+(reason_code,)))))
        self._jobs[job_id]=u
        return u

    def get(self, job_id: UUID) -> ResearchJob:
        return self._jobs[job_id]
