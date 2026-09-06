class PortfolioManager:
    def __init__(self):
        self.positions = {}

    def set_position(self, symbol, qty):
        self.positions[symbol] = qty
        return self.positions
