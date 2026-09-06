from __future__ import annotations
from decimal import Decimal
from omega_strategy.domain.models import (
    StrategyProposal, ProposalClass, RouterDecision
)
from omega_strategy.scoring.model import score_proposal
from omega_strategy.lifecycle.permissions import can_produce_live_candidate

CLASS_PRIORITY = {
    ProposalClass.PROTECTIVE: 5,
    ProposalClass.EXIT: 4,
    ProposalClass.HEDGE: 3,
    ProposalClass.ENTRY: 2,
    ProposalClass.WAIT: 1,
}

class MetaRouter:
    def __init__(
        self,
        registry,
        *,
        minimum_entry_score: Decimal = Decimal("0.65"),
        minimum_score_gap_for_direction_conflict: Decimal = Decimal("0.12"),
    ) -> None:
        self.registry = registry
        self.minimum_entry_score = minimum_entry_score
        self.minimum_score_gap_for_direction_conflict = minimum_score_gap_for_direction_conflict

    def route(self, proposals: list[StrategyProposal]) -> RouterDecision:
        if not proposals:
            return RouterDecision(None,None,"WAIT",Decimal("0"),("STRAT_WAIT",),(),False)

        # Highest proposal class first.
        max_priority = max(CLASS_PRIORITY[p.proposal_class] for p in proposals)
        cohort = [p for p in proposals if CLASS_PRIORITY[p.proposal_class] == max_priority]

        scored = [(p, score_proposal(p).final_score) for p in cohort]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Protective/exit always outrank entry and may be selected even below entry threshold.
        if cohort[0].proposal_class in {ProposalClass.PROTECTIVE, ProposalClass.EXIT}:
            p, s = scored[0]
            desc = self.registry.get(p.strategy_id).descriptor
            return RouterDecision(
                p.proposal_id, p.strategy_id, p.action.value, s,
                ("STRAT_PROTECTIVE_PRIORITY",) if p.proposal_class is ProposalClass.PROTECTIVE else (),
                tuple(x.proposal_id for x in proposals),
                can_produce_live_candidate(desc),
            )

        # Detect LONG/SHORT conflict for entry/hedge.
        directional = [(p,s) for p,s in scored if p.side in {"BUY","SELL"}]
        sides = {p.side for p,_ in directional}
        if len(sides) > 1:
            top_p, top_s = directional[0]
            second_p, second_s = directional[1]
            if top_p.side != second_p.side and (top_s - second_s) < self.minimum_score_gap_for_direction_conflict:
                return RouterDecision(
                    None,None,"WAIT",Decimal("0"),
                    ("STRAT_DIRECTION_CONFLICT","STRAT_CONFLICT_TOO_CLOSE"),
                    tuple(x.proposal_id for x in proposals),
                    False,
                )

        p, s = scored[0]
        if p.proposal_class is ProposalClass.ENTRY and s < self.minimum_entry_score:
            return RouterDecision(
                None,None,"WAIT",s,("STRAT_SCORE_TOO_LOW","STRAT_WAIT"),
                tuple(x.proposal_id for x in proposals),False
            )

        desc = self.registry.get(p.strategy_id).descriptor
        live_candidate = can_produce_live_candidate(desc)
        reasons = []
        if not live_candidate:
            reasons.append("STRAT_LIVE_PERMISSION_DENIED")
        return RouterDecision(
            p.proposal_id,p.strategy_id,p.action.value,s,
            tuple(reasons),tuple(x.proposal_id for x in proposals),live_candidate
        )
