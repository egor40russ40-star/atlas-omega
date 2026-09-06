class BacktestFarm:
    def run(self, strategy, history):
        return {"strategy":strategy,"bars":len(history),"status":"COMPLETED"}
