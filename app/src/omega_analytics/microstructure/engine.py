class MicrostructureEngine:
    def analyze(self, orderbook):
        return {
            "spread": orderbook.get("spread", 0),
            "pressure": orderbook.get("pressure", "UNKNOWN")
        }
