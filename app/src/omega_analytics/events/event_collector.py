from datetime import datetime, timezone


class EventCollector:
    """
    Центральный сборщик событий ATLAS OMEGA.
    """

    def __init__(self):
        self.events = []

    def emit(
        self,
        *,
        instrument: str,
        strategy: str,
        event_type: str,
        price: float | None = None,
        reason: str = "",
        metadata: dict | None = None,
    ):

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "instrument": instrument,
            "strategy": strategy,
            "event_type": event_type,
            "price": price,
            "reason": reason,
            "metadata": metadata or {},
        }

        self.events.append(event)

        return event

    def all_events(self):
        return self.events