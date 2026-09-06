class HistoricalLoader:
    def load(self, symbol, timeframe):
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "status": "READY_FOR_BACKTEST"
        }
