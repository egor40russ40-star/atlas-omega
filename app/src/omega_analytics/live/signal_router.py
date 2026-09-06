class SignalRouter:
    def route(self, signal):
        return "ALLOW" if signal.confidence == "HIGH" else "WAIT"
