class MarketUniverseEngine:
    def __init__(self):
        self.instruments = []
    def add(self, symbol, kind):
        self.instruments.append({"symbol":symbol,"kind":kind})
    def all(self):
        return self.instruments
