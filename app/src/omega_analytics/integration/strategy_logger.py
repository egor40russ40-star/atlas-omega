from .signal_context import SignalContext


class StrategyLogger:

    def __init__(self, repository):
        self.repository = repository

    def log_signal(self, context: SignalContext):

        return self.repository.save_signal(context)