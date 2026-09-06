class CapitalManager:
    def __init__(self, capital=0):
        self.capital = capital

    def allocation(self, risk):
        return self.capital * risk
