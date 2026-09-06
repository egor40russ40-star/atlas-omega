class FusionEngine:
    def combine(self, signals):
        if not signals:
            return None
        return max(signals, key=lambda x:x.get("score",0))
