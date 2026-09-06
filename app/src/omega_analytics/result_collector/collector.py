class ResultCollector:
    def __init__(self):
        self.results = []

    def add(self, result):
        self.results.append(result)

    def get_all(self):
        return self.results
