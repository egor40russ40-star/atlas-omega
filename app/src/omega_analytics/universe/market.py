class MarketUniverse:
    def __init__(self):
        self.instruments = []

    def add(self, symbol):
        self.instruments.append(symbol)

    def all(self):
        return self.instruments
