class DataNormalizer:
    def normalize(self, candle):
        return {
            "symbol": candle.get("symbol"),
            "timestamp": candle.get("timestamp"),
            "open": candle.get("open"),
            "high": candle.get("high"),
            "low": candle.get("low"),
            "close": candle.get("close"),
            "volume": candle.get("volume")
        }
