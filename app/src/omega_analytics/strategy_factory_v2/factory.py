class StrategyFactoryV2:
    def __init__(self):
        self.strategies = {}

    def register(self, name, strategy):
        self.strategies[name] = strategy

    def select(self, regime):
        return self.strategies.get(regime)
