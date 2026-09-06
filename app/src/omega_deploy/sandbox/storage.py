from __future__ import annotations
from pathlib import Path
import sqlite3, json
from datetime import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS sandbox_runs (
    run_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    instrument_id TEXT NOT NULL,
    state TEXT NOT NULL,
    stage TEXT NOT NULL,
    result_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sandbox_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
"""

class SandboxJournal:
    def __init__(self,path: str | Path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.conn=sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def append_event(self,run_id: str,event_type: str,payload: dict,*,occurred_at: datetime):
        self.conn.execute(
            "INSERT INTO sandbox_events(run_id,occurred_at,event_type,payload_json) VALUES(?,?,?,?)",
            (run_id,occurred_at.isoformat(),event_type,json.dumps(payload,ensure_ascii=False,default=str))
        )
        self.conn.commit()

    def save_run(self,run_id: str,instrument_id: str,state: str,stage: str,result: dict,*,created_at: datetime):
        self.conn.execute(
            """INSERT INTO sandbox_runs(run_id,created_at,instrument_id,state,stage,result_json)
               VALUES(?,?,?,?,?,?)
               ON CONFLICT(run_id) DO UPDATE SET state=excluded.state,stage=excluded.stage,result_json=excluded.result_json""",
            (run_id,created_at.isoformat(),instrument_id,state,stage,json.dumps(result,ensure_ascii=False,default=str))
        )
        self.conn.commit()

    def latest_runs(self,limit: int=10):
        rows=self.conn.execute(
            "SELECT run_id,created_at,instrument_id,state,stage,result_json FROM sandbox_runs ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return tuple({
            "run_id":r[0],"created_at":r[1],"instrument_id":r[2],"state":r[3],"stage":r[4],
            "result":json.loads(r[5])
        } for r in rows)

    def close(self):
        self.conn.close()
