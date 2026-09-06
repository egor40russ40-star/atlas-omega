import sqlite3
from pathlib import Path


class ResearchDatabase:
    """
    Хранилище результатов исследований стратегий.
    """

    def __init__(
        self,
        db_path="omega_research.sqlite3",
    ):
        self.db_path = Path(db_path)

        self.connection = sqlite3.connect(
            self.db_path
        )


    def initialize(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS research_results
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                strategy TEXT NOT NULL,

                trades INTEGER,
                wins INTEGER,
                losses INTEGER,

                total_pnl REAL,
                average_r REAL,
                win_rate REAL
            )
            """
        )

        self.connection.commit()


    def save(self, record):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO research_results
            (
                strategy,
                trades,
                wins,
                losses,
                total_pnl,
                average_r,
                win_rate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.strategy,
                record.trades,
                record.wins,
                record.losses,
                record.total_pnl,
                record.average_r,
                record.win_rate,
            ),
        )

        self.connection.commit()


    def all_results(self):

        cursor = self.connection.cursor()

        return cursor.execute(
            """
            SELECT *
            FROM research_results
            """
        ).fetchall()