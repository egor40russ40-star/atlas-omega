class ExecutionGateway:
    def __init__(self, provider=None):
        self.provider = provider

    def send(self, signal):
        return {
            "status": "SIMULATED",
            "signal": signal,
        }
