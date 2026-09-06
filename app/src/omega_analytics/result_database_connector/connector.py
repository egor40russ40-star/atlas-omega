class ResearchResultDatabaseConnector:
    def __init__(self):
        self.results = []
        self.runs = []

    def register_run(self, run_id, metadata=None):
        self.runs.append({
            'run_id': run_id,
            'metadata': metadata or {}
        })

    def save_result(self, result):
        self.results.append(result)

    def get_results(self):
        return self.results

    def get_runs(self):
        return self.runs
