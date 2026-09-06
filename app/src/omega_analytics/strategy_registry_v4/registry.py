class StrategyRegistryV4:
    def __init__(self):
        self.strategies = []

    def add(self, name, version):
        self.strategies.append({'name': name, 'version': version})

    def all(self):
        return self.strategies
