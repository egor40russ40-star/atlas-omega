from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping, Any, Optional
from uuid import UUID

class HypothesisState(str, Enum):
    IDEA = "IDEA"
    DRAFT = "DRAFT"
    APPROVED_FOR_RESEARCH = "APPROVED_FOR_RESEARCH"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    EVALUATED = "EVALUATED"
    CANDIDATE = "CANDIDATE"
    SUBMITTED_TO_VALIDATION = "SUBMITTED_TO_VALIDATION"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"

class AuthorType(str, Enum):
    HUMAN = "HUMAN"
    AI = "AI"
    SYSTEM = "SYSTEM"

class ExperimentType(str, Enum):
    BASELINE = "BASELINE"
    CANDIDATE = "CANDIDATE"
    ROBUSTNESS = "ROBUSTNESS"
    WALK_FORWARD = "WALK_FORWARD"
    ADVERSARIAL = "ADVERSARIAL"
    SHADOW_PLAN = "SHADOW_PLAN"
    SANDBOX_PLAN = "SANDBOX_PLAN"

class JobState(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class CandidateState(str, Enum):
    LAB = "LAB"
    SUBMITTED_TO_VALIDATION = "SUBMITTED_TO_VALIDATION"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"

@dataclass(frozen=True, slots=True)
class Hypothesis:
    hypothesis_id: UUID
    title_ru: str
    problem_statement: str
    instrument_id: str
    strategy_family: str
    evidence_ids: tuple[str, ...]
    expected_mechanism: str
    falsifiable_prediction: str
    proposed_change: Mapping[str, Any]
    target_metrics: tuple[str, ...]
    risks: tuple[str, ...]
    required_experiments: tuple[ExperimentType, ...]
    author_type: AuthorType
    priority: int
    state: HypothesisState
    created_at: datetime
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class ExperimentSpec:
    experiment_id: UUID
    hypothesis_id: UUID
    experiment_type: ExperimentType
    strategy_family: str
    parent_strategy_version: str
    candidate_config: Mapping[str, Any]
    dataset_id: str
    dataset_hash: str
    random_seed: int
    required_validation: tuple[str, ...]
    resource_cost_estimate: Mapping[str, Decimal]
    created_at: datetime
    baseline_experiment_id: Optional[UUID] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class ResearchJob:
    job_id: UUID
    experiment_id: UUID
    state: JobState
    priority: int
    queued_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    reason_codes: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class MutableParameter:
    name: str
    baseline: Decimal
    minimum: Decimal
    maximum: Decimal
    step: Decimal
    research_only: bool = True

@dataclass(frozen=True, slots=True)
class Mutation:
    parameter: str
    old_value: Decimal
    new_value: Decimal
    mutation_type: str

@dataclass(frozen=True, slots=True)
class StrategyGenome:
    family: str
    parent_ids: tuple[str, ...]
    generation: int
    parameters: Mapping[str, Decimal]
    mutation_history: tuple[Mutation, ...]
    random_seed: int

@dataclass(frozen=True, slots=True)
class StrategyCandidate:
    candidate_id: UUID
    hypothesis_id: UUID
    family: str
    parent_versions: tuple[str, ...]
    generation: int
    genome_hash: str
    config_hash: str
    code_hash: str
    state: CandidateState
    created_at: datetime
    changes: tuple[Mapping[str, Any], ...]
    validation_plan: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class OverfitEvidence:
    trades: int
    walkforward_folds: int
    best_fold_profit_share: Decimal
    cost_robustness_ratio: Decimal
    neighbour_parameter_pass_rate: Decimal
    leakage_violations: int
    reproducible: bool

@dataclass(frozen=True, slots=True)
class OverfitDecision:
    passed: bool
    reason_codes: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class ValidationSubmission:
    submission_id: UUID
    candidate_id: UUID
    submitted_at: datetime
    digital_twin_plan_id: str
    required_gates: tuple[str, ...]
    manifest_hash: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
