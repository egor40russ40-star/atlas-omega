class StrategyMemory:
    def __init__(self):
        self.history=[]
    def add(self, item):
        self.history.append(item)
