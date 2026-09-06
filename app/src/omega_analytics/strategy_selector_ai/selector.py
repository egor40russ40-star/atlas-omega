class StrategySelectorAI:
    def select(self, candidates):
        if not candidates:
            return None
        return max(candidates, key=lambda x:x.get("score",0))
