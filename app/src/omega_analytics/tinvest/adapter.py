class TInvestAdapter:
    def connect(self):
        return True

    def get_market_data(self, symbol):
        return {"symbol": symbol, "mode": "paper"}
