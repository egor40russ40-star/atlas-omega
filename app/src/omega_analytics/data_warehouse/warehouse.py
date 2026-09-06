class DataWarehouse:
    def __init__(self):
        self.datasets = {}

    def save(self, name, data):
        self.datasets[name] = data

    def load(self, name):
        return self.datasets.get(name)
