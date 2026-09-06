import sqlite3
from pathlib import Path

from .schema import ANALYTICS_SCHEMA


class AnalyticsStorage:

    def __init__(self, db_path="omega_analytics.sqlite3"):
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(self.db_path)

    def initialize(self):
        cursor = self.connection.cursor()

        for name, sql in ANALYTICS_SCHEMA.items():
            cursor.execute(sql)

        self.connection.commit()

    def execute(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def close(self):
        self.connection.close()