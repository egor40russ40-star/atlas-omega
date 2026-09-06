from __future__ import annotations
from dataclasses import replace
from decimal import Decimal
import random
from omega_research.domain.models import MutableParameter, Mutation, StrategyGenome
from omega_research.genetics.guard import validate_mutable_parameter

def mutate_one(
    genome: StrategyGenome,
    parameter: MutableParameter,
    *,
    seed: int,
) -> StrategyGenome:
    validate_mutable_parameter(parameter)
    current=genome.parameters.get(parameter.name,parameter.baseline)
    rng=random.Random(seed)
    direction=rng.choice([-1,1])
    new=current + parameter.step*Decimal(direction)
    if new < parameter.minimum or new > parameter.maximum:
        new=current - parameter.step*Decimal(direction)
    if new < parameter.minimum or new > parameter.maximum:
        raise ValueError("RESEARCH_MUTATION_OUT_OF_BOUNDS")
    params=dict(genome.parameters)
    params[parameter.name]=new
    mutation=Mutation(parameter.name,current,new,"MUTATE_PARAMETER")
    return StrategyGenome(
        genome.family,
        genome.parent_ids,
        genome.generation+1,
        params,
        genome.mutation_history+(mutation,),
        seed,
    )
