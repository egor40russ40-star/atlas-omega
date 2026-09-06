class StrategyMatrix:
    def generate(self, instruments, strategies):
        return [
            {"instrument": i, "strategy": s}
            for i in instruments for s in strategies
        ]
