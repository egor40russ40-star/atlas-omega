from omega_strategy.domain.models import StrategyDescriptor, StrategyRole
from omega_strategy.strategies.common import wait_proposal

class ScalperV1:
    descriptor = StrategyDescriptor(
        "SCALPER_V1","Скальпер v1","*",
        StrategyRole.LAB,"SCALPER","1",
        live_permission=False,sandbox_only=True,independent_family="SCALPER"
    )
    def evaluate(self, world_model, context):
        return wait_proposal(
            self.descriptor,world_model,context,
            ["STRAT_SCALPER_SANDBOX_ONLY","STRAT_WAIT"]
        )
