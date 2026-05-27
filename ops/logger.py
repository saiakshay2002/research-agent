import sqlite3
import time
import json
from pathlib import Path
from datetime import datetime


DB_PATH = Path("./ops/queries.db")


class QueryLogger:
    def __init__(self, db_path: Path = DB_PATH):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT    NOT NULL,
                query       TEXT    NOT NULL,
                tools_used  TEXT    NOT NULL,
                latency_ms  REAL    NOT NULL,
                token_count INTEGER,
                success     INTEGER NOT NULL,
                answer_len  INTEGER
            )
        """)
        self.conn.commit()

    def log(
        self,
        query: str,
        tools_used: list,
        latency_ms: float,
        token_count: int = 0,
        success: bool = True,
        answer_len: int = 0,
    ):
        self.conn.execute(
            """INSERT INTO queries
               (timestamp, query, tools_used, latency_ms, token_count, success, answer_len)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.utcnow().isoformat(),
                query,
                json.dumps(tools_used),
                latency_ms,
                token_count,
                int(success),
                answer_len,
            ),
        )
        self.conn.commit()

    def fetch_all(self) -> list:
        cursor = self.conn.execute(
            "SELECT * FROM queries ORDER BY id DESC LIMIT 200"
        )
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def summary_stats(self) -> dict:
        cursor = self.conn.execute("""
            SELECT
                COUNT(*)           AS total_queries,
                AVG(latency_ms)    AS avg_latency_ms,
                MIN(latency_ms)    AS min_latency_ms,
                MAX(latency_ms)    AS max_latency_ms,
                SUM(token_count)   AS total_tokens,
                SUM(success)       AS successful,
                COUNT(*) - SUM(success) AS failed
            FROM queries
        """)
        row = cursor.fetchone()
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))
