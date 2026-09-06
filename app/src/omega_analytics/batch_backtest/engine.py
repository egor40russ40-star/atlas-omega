class BatchBacktest:
    def run(self, matrix):
        return [{"test":x,"status":"READY"} for x in matrix]
