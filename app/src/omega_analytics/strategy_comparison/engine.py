class StrategyComparison:
    def compare(self, results):
        return sorted(
            results,
            key=lambda x: x.get('score', 0),
            reverse=True
        )
