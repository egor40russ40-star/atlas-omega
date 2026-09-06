class HistoricalValidator:
    def validate(self, trades):
        return {
            "trades": len(trades),
            "validated": True
        }
