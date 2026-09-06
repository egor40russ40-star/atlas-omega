class MetricsStorage:
    def __init__(self):
        self.metrics = []

    def save(self, strategy, instrument, metrics):
        self.metrics.append({
            'strategy': strategy,
            'instrument': instrument,
            'metrics': metrics
        })

    def all(self):
        return self.metrics
