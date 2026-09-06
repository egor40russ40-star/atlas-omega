class ResearchIntegration:
    def __init__(self, mode="RESEARCH_PC"):
        self.mode = mode
        self.components = []

    def register(self, component):
        self.components.append(component)

    def status(self):
        return {
            "mode": self.mode,
            "components": len(self.components),
            "trading_enabled": False
        }
