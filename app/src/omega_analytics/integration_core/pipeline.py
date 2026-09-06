class TradingPipeline:
    def __init__(self, steps=None):
        self.steps = steps or []

    def run(self, data):
        result = data
        for step in self.steps:
            result = step(result)
        return result
