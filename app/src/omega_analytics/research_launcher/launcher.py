class FirstResearchLauncher:
    def __init__(self, campaign=None):
        self.campaign = campaign or {}
        self.status = "READY"

    def start(self):
        self.status = "RUNNING"
        return {
            "status": self.status,
            "campaign": self.campaign
        }

    def finish(self, report=None):
        self.status = "COMPLETED"
        return {
            "status": self.status,
            "report": report or {}
        }
