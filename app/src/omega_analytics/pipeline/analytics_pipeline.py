from omega_analytics.integration.signal_context import SignalContext
from omega_analytics.integration.trade_context import TradeContext


class AnalyticsPipeline:
    """
    Центральный поток аналитики ATLAS OMEGA.

    Принимает:
    - торговые сигналы
    - контекст сделок

    Передает:
    - в журнал аналитики
    - в хранилище
    """

    def __init__(self, repository):
        self.repository = repository

    def process_signal(self, context: SignalContext):
        """
        Сохраняет торговый сигнал.
        """
        return self.repository.save_signal(context)

    def process_trade(self, context: TradeContext):
        """
        Сохраняет результат сделки.
        """
        return self.repository.save_trade(context)