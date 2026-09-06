class BacktestStorage:
    def __init__(self):
        self.results=[]

    def save(self, result):
        self.results.append(result)

    def all(self):
        return self.results
