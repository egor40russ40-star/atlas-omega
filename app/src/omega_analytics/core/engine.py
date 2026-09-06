class AnalyticsCoreEngine:
    def __init__(self, analyzer=None, decision=None):
        self.analyzer = analyzer
        self.decision = decision

    def process(self, data):
        analysis = self.analyzer.analyze(data) if self.analyzer else data
        return self.decision.evaluate(analysis) if self.decision else analysis
