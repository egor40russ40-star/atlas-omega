class PositionManager:
    def __init__(self):
        self.positions={}

    def update(self, symbol, qty):
        self.positions[symbol]=qty
        return self.positions
