import json


class EventRepository:
    """
    Хранилище событий Analytics Engine.
    """

    def __init__(self, storage):
        self.storage = storage

    def initialize(self):

        self.storage.execute(
            """
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                instrument TEXT NOT NULL,
                strategy TEXT NOT NULL,
                event_type TEXT NOT NULL,
                price REAL,
                reason TEXT,
                metadata TEXT
            )
            """
        )

    def save_event(self, event: dict):

        self.storage.execute(
            """
            INSERT INTO analytics_events(
                timestamp,
                instrument,
                strategy,
                event_type,
                price,
                reason,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["timestamp"],
                event["instrument"],
                event["strategy"],
                event["event_type"],
                event.get("price"),
                event.get("reason"),
                json.dumps(event.get("metadata", {})),
            ),
        )

    def get_events(self):

        cursor = self.storage.execute(
            """
            SELECT
                timestamp,
                instrument,
                strategy,
                event_type,
                price,
                reason
            FROM analytics_events
            ORDER BY id
            """
        )

        return cursor.fetchall()