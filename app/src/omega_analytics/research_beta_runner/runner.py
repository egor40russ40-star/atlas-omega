class ResearchBetaRunner:
    def __init__(self, executor):
        self.executor = executor
        self.results = []

    def run_batch(self, tasks):
        self.results = [self.executor.execute(task) for task in tasks]
        return self.results

    def progress(self):
        return {
            'total': len(self.results),
            'completed': len([r for r in self.results if r.get('status') == 'COMPLETED'])
        }
