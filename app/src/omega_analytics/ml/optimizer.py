class StrategyOptimizer:
    def rank(self, strategies):
        return sorted(strategies, key=lambda x: x.get('score',0), reverse=True)
