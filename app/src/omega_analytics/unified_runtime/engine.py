class UnifiedRuntime:
    def __init__(self, services=None):
        self.services = services or []
        self.state = "INIT"
    def start(self):
        self.state = "RUNNING"
        return self.state
    def stop(self):
        self.state = "STOPPED"
        return self.state
