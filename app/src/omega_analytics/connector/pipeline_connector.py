from omega_analytics.pipeline import AnalyticsPipeline
from omega_analytics.integration.signal_context import SignalContext


class AnalyticsPipelineConnector:
    """
    Связующий слой между стратегическими адаптерами
    и Analytics Pipeline.
    """

    def __init__(self, pipeline: AnalyticsPipeline):
        self.pipeline = pipeline

    def submit_signal(self, signal: SignalContext):
        """
        Передача сигнала в аналитический контур.
        """
        return self.pipeline.process_signal(signal)