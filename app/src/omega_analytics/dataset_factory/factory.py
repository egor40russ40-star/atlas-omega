class DatasetFactory:
    def create(self, symbol, timeframe, period):
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "period": period
        }
