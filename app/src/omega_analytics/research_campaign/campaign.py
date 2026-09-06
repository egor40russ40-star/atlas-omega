class ResearchCampaign:
    def __init__(self):
        self.instruments = []
        self.strategies = []

    def configure(self, instruments, strategies):
        self.instruments = instruments
        self.strategies = strategies

    def summary(self):
        return {
            "instruments": len(self.instruments),
            "strategies": len(self.strategies)
        }
