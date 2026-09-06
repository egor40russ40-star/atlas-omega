class ApprovedStrategyStore:
    def __init__(self):
        self.items=[]
    def add(self, strategy):
        self.items.append(strategy)
