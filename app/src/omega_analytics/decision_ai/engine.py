class AIDecisionEngine:
    def decide(self, signal, risk_ok=True):
        if not risk_ok:
            return "BLOCK"
        return "ALLOW" if signal else "WAIT"
