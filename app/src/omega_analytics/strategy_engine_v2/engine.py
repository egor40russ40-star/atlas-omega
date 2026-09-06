class StrategyEngineV2:
    def __init__(self):
        self.strategies=[]

    def register(self, strategy):
        self.strategies.append(strategy)

    def available(self):
        return self.strategies
