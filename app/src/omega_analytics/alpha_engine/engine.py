class AlphaEngine:
    def score(self, signal):
        return signal.get('score',0) if isinstance(signal,dict) else 0
