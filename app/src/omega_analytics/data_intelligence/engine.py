class DataIntelligence:
    def __init__(self):
        self.datasets = {}

    def register_dataset(self, name, data):
        self.datasets[name] = data

    def get_dataset(self, name):
        return self.datasets.get(name)
