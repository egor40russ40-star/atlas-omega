class ResearchFactory:
    def run(self, universe, strategies):
        return [{'instrument':i,'strategy':s} for i in universe for s in strategies]
