from __future__ import annotations
from typing import Protocol
from omega_research.domain.models import ValidationSubmission

class ValidationLabPort(Protocol):
    def submit(self, submission: ValidationSubmission) -> str: ...
