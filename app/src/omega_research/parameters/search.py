from __future__ import annotations
from decimal import Decimal
from itertools import product
from typing import Mapping, Iterable
from omega_research.domain.models import MutableParameter

def values_for_parameter(p: MutableParameter) -> tuple[Decimal,...]:
    if p.step <= 0 or p.minimum > p.maximum:
        raise ValueError("invalid mutable parameter")
    vals=[]
    x=p.minimum
    # Safe for small research grids.
    while x <= p.maximum:
        vals.append(x)
        x += p.step
    return tuple(vals)

def grid_candidates(parameters: Iterable[MutableParameter], *, max_candidates: int = 500) -> tuple[dict[str,Decimal],...]:
    ps=list(parameters)
    spaces=[values_for_parameter(p) for p in ps]
    out=[]
    for combo in product(*spaces):
        out.append({p.name:v for p,v in zip(ps,combo)})
        if len(out)>=max_candidates:
            break
    return tuple(out)

def local_neighbours(parameters: Iterable[MutableParameter], baseline: Mapping[str,Decimal]) -> tuple[dict[str,Decimal],...]:
    out=[]
    for p in parameters:
        base=baseline[p.name]
        for candidate in (base-p.step,base+p.step):
            if p.minimum <= candidate <= p.maximum:
                c=dict(baseline); c[p.name]=candidate; out.append(c)
    return tuple(out)
