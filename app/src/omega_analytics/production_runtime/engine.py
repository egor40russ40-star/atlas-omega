class ProductionRuntime:
    def __init__(self, mode="PAPER"):
        self.mode = mode
        self.running = False

    def start(self):
        self.running = True
        return {"mode": self.mode, "status": "RUNNING"}

    def stop(self):
        self.running = False
        return {"status": "STOPPED"}
