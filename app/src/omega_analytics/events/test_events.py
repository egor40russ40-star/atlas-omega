import sys

sys.path.insert(
    0,
    r"C:\Users\test4\atlas-omega-work\atlas-omega\app\src"
)

from omega_analytics.storage import AnalyticsStorage
from omega_analytics.events import EventCollector, EventRepository


storage = AnalyticsStorage("events_test.sqlite3")
storage.initialize()

repo = EventRepository(storage)
repo.initialize()

collector = EventCollector()

event = collector.emit(
    instrument="ROSN",
    strategy="ROSN_HEDGE_V3",
    event_type="ENTRY",
    price=319.0,
    reason="support_retest",
    metadata={
        "timeframe": "5m",
        "risk": "1R"
    }
)

repo.save_event(event)

print(repo.get_events())

print("EVENT SAVE TEST OK")