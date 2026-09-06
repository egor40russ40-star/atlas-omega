from .strategy_evaluator import StrategyEvaluator


class ResearchOrchestrator:

    def __init__(self):
        self.evaluator = StrategyEvaluator()


    def analyze(self, replay_report):

        return self.evaluator.evaluate(
            replay_report
        )