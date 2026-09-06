class SimulationRunner:
    def run(self, pipeline, data):
        results = []
        for item in data:
            results.append(pipeline.process(item))
        return results
