class ResearchExecutor:
    def __init__(self):
        self.results = []

    def execute(self, task):
        result = {
            'task': task,
            'status': 'COMPLETED'
        }
        self.results.append(result)
        return result

    def all_results(self):
        return self.results
