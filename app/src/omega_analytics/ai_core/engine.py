class AITradingCore:
    def __init__(self, modules=None):
        self.modules = modules or []

    def run_cycle(self, market):
        return {"status":"ANALYZED","market":market}
