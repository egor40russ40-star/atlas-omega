from omega_strategy.domain.models import StrategyDescriptor, StrategyRole
from omega_strategy.strategies.common import wait_proposal

class OrderFlowSetupStrategy:
    descriptor = StrategyDescriptor(
        "ORDERFLOW_SETUP_V1","Стакан и поток заявок","*",
        StrategyRole.LAB,"ORDERFLOW","1",
        live_permission=False,independent_family="ORDERFLOW"
    )
    def evaluate(self, world_model, context):
        if world_model.orderflow is None:
            return wait_proposal(self.descriptor,world_model,context,["STRAT_WAIT"])
        return wait_proposal(self.descriptor,world_model,context,["STRAT_WAIT"])
