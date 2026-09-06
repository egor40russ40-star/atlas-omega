from __future__ import annotations
from decimal import Decimal
from typing import Iterable
from omega_market_brain.domain.models import ContextNode, ContextGraphState

def build_context_graph(instrument_id: str, nodes: Iterable[ContextNode]) -> ContextGraphState:
    ns = tuple(nodes)
    if not ns:
        return ContextGraphState(
            instrument_id, (), Decimal("0"), Decimal("1"), Decimal("0"),
            ("BRAIN_EXTERNAL_CONTEXT_STALE",)
        )

    weighted = Decimal("0")
    total_w = Decimal("0")
    signs = []
    freshness_sum = Decimal("0")

    for n in ns:
        w = max(Decimal("0"), min(n.confidence * n.freshness * n.source_quality, Decimal("1")))
        weighted += n.direction * w
        total_w += w
        freshness_sum += n.freshness
        if w > Decimal("0.15") and n.direction != 0:
            signs.append(Decimal("1") if n.direction > 0 else Decimal("-1"))

    aggregate = Decimal("0") if total_w == 0 else weighted / total_w
    freshness = freshness_sum / Decimal(len(ns))
    conflict = Decimal("0")
    if signs:
        pos = sum(1 for s in signs if s > 0)
        neg = sum(1 for s in signs if s < 0)
        conflict = Decimal(min(pos, neg)) / Decimal(max(pos, neg)) if max(pos, neg) else Decimal("0")

    reasons = []
    if freshness < Decimal("0.6"):
        reasons.append("BRAIN_EXTERNAL_CONTEXT_STALE")
    if conflict > Decimal("0.5"):
        reasons.append("BRAIN_CONTEXT_CONFLICT")

    return ContextGraphState(
        instrument_id=instrument_id,
        nodes=ns,
        aggregate_score=max(Decimal("-1"), min(aggregate, Decimal("1"))),
        conflict_score=min(conflict, Decimal("1")),
        freshness_score=max(Decimal("0"), min(freshness, Decimal("1"))),
        reason_codes=tuple(sorted(set(reasons))),
    )
