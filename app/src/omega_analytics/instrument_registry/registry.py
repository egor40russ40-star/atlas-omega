class InstrumentRegistry:
    def __init__(self):
        self.items = []

    def register(self, symbol, kind):
        self.items.append({'symbol': symbol, 'kind': kind})

    def all(self):
        return self.items
