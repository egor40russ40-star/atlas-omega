class ResearchExecutionPipeline:
    def __init__(self, executor):
        self.executor = executor

    def run(self, tasks):
        return [self.executor.execute(task) for task in tasks]
