class StrategyRegistryV3:
    def __init__(self):
        self.items={}

    def register(self,name,strategy):
        self.items[name]=strategy

    def all(self):
        return self.items
