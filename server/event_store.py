"""SQLite event memory for AuraAssist."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("./aura_assist.db")


class EventStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init()

    def _init(self):
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                event_type TEXT NOT NULL,
                room TEXT,
                device_id TEXT,
                action TEXT,
                details TEXT,
                confidence REAL
            )
            """
        )
        self._conn.commit()

    def add_event(
        self,
        event_type: str,
        room: Optional[str] = None,
        device_id: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO events (ts, event_type, room, device_id, action, details, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, event_type, room, device_id, action, details, confidence),
        )
        self._conn.commit()
        return cur.lastrowid

    def get_recent(
        self,
        since: Optional[str] = None,
        room: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        clauses = []
        params: List[Any] = []
        if since:
            clauses.append("ts >= ?")
            params.append(since)
        if room:
            clauses.append("lower(room)=lower(?)")
            params.append(room)
        if event_type:
            clauses.append("event_type=?")
            params.append(event_type)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        sql = f"SELECT * FROM events {where} ORDER BY ts DESC LIMIT ?"
        params.append(limit)
        rows = cur.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def find_object(self, object_name: str, time_range: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        clauses = ["event_type='object_sighting'"]
        params: List[Any] = []
        if object_name:
            clauses.append("lower(details) LIKE ?")
            params.append(f"%{object_name.lower()}%")
        if time_range:
            clauses.append("ts >= ?")
            params.append(time_range)
        where = " WHERE " + " AND ".join(clauses)
        sql = f"SELECT * FROM events {where} ORDER BY ts DESC LIMIT ?"
        params.append(limit)
        rows = cur.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


event_store = EventStore()
