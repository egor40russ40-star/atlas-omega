from __future__ import annotations
from dataclasses import replace
from uuid import UUID
from omega_research.domain.models import Hypothesis, HypothesisState

class HypothesisRegistry:
    def __init__(self) -> None:
        self._items: dict[UUID,Hypothesis] = {}

    def add(self, hypothesis: Hypothesis) -> None:
        if hypothesis.hypothesis_id in self._items:
            if self._items[hypothesis.hypothesis_id] != hypothesis:
                raise ValueError("hypothesis immutable")
            return
        self._items[hypothesis.hypothesis_id]=hypothesis

    def get(self, hypothesis_id: UUID) -> Hypothesis:
        return self._items[hypothesis_id]

    def transition(self, hypothesis_id: UUID, new_state: HypothesisState) -> Hypothesis:
        current=self._items[hypothesis_id]
        allowed={
            HypothesisState.IDEA:{HypothesisState.DRAFT,HypothesisState.ARCHIVED},
            HypothesisState.DRAFT:{HypothesisState.APPROVED_FOR_RESEARCH,HypothesisState.REJECTED,HypothesisState.ARCHIVED},
            HypothesisState.APPROVED_FOR_RESEARCH:{HypothesisState.QUEUED,HypothesisState.REJECTED},
            HypothesisState.QUEUED:{HypothesisState.RUNNING,HypothesisState.REJECTED},
            HypothesisState.RUNNING:{HypothesisState.EVALUATED,HypothesisState.REJECTED},
            HypothesisState.EVALUATED:{HypothesisState.CANDIDATE,HypothesisState.REJECTED,HypothesisState.ARCHIVED},
            HypothesisState.CANDIDATE:{HypothesisState.SUBMITTED_TO_VALIDATION,HypothesisState.REJECTED},
            HypothesisState.SUBMITTED_TO_VALIDATION:{HypothesisState.ARCHIVED},
            HypothesisState.REJECTED:{HypothesisState.ARCHIVED},
            HypothesisState.ARCHIVED:set(),
        }
        if new_state not in allowed[current.state]:
            raise ValueError(f"invalid hypothesis transition: {current.state.value}->{new_state.value}")
        updated=replace(current,state=new_state)
        self._items[hypothesis_id]=updated
        return updated
