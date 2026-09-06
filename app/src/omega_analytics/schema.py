from dataclasses import dataclass


ANALYTICS_SCHEMA = {

    "trades": """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            strategy TEXT NOT NULL,
            side TEXT NOT NULL,

            entry_price REAL,
            exit_price REAL,
            quantity REAL,

            pnl REAL,
            commission REAL DEFAULT 0,
            slippage REAL DEFAULT 0,

            r_multiple REAL,

            entry_time TEXT,
            exit_time TEXT,

            status TEXT
        );
    """,


    "signals": """
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT NOT NULL,
            strategy TEXT NOT NULL,

            timeframe TEXT,

            signal_type TEXT,
            confidence REAL,

            regime TEXT,
            volatility TEXT,

            reason TEXT,

            created_at TEXT
        );
    """,


    "executions": """
        CREATE TABLE IF NOT EXISTS executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id TEXT,

            symbol TEXT,

            requested_price REAL,
            executed_price REAL,

            latency_ms REAL,

            status TEXT,

            created_at TEXT
        );
    """,


    "performance": """
        CREATE TABLE IF NOT EXISTS performance_snapshots (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            equity REAL,

            trades_count INTEGER,

            winrate REAL,

            profit_factor REAL,

            expectancy REAL,

            drawdown REAL,

            created_at TEXT
        );
    """
}