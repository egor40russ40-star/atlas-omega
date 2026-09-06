class RiskEngine:
    def __init__(self, limits=None):
        self.limits = limits or {}

    def check(self, symbol, exposure):
        limit = self.limits.get(symbol)
        if limit is None:
            return True
        return exposure <= limit
