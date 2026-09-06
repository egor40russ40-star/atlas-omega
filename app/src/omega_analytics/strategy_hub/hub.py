class StrategyHub:
    def __init__(self):
        self.strategies = {}
    def register(self, name, strategy):
        self.strategies[name] = strategy
    def list(self):
        return list(self.strategies.keys())
