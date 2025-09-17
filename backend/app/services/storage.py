"""
storage.py
یک storage ساده مبتنی بر sqlite برای ذخیره rules و processed comments
(Simple SQLite-backed storage for rules and processed comments)
"""

import sqlite3
import threading
import json
import time
from typing import List, Dict, Optional

DB_FILE = "./storage.db"

lock = threading.Lock()

class Storage:
    """
    Storage
    - مدیریت ساده روی SQLite: جداول rules و processed_comments
    """
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self._init_db()

    def _init_db(self):
        with lock, sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_id TEXT NOT NULL,
                patterns TEXT NOT NULL, -- JSON array
                reply_text TEXT,
                direct_text TEXT,
                cooldown_seconds INTEGER DEFAULT 3600
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS processed_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comment_id TEXT UNIQUE,
                media_id TEXT,
                processed_at INTEGER
            );
            """)
            conn.commit()

    def add_rule(self, media_id: str, patterns: List[str], reply_text: str, direct_text: str, cooldown_seconds: int = 3600) -> int:
        with lock, sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO rules (media_id, patterns, reply_text, direct_text, cooldown_seconds) VALUES (?, ?, ?, ?, ?)",
                        (media_id, json.dumps(patterns, ensure_ascii=False), reply_text, direct_text, cooldown_seconds))
            conn.commit()
            return cur.lastrowid

    def list_rules(self, media_id: Optional[str] = None) -> List[Dict]:
        with lock, sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            if media_id:
                cur.execute("SELECT id, media_id, patterns, reply_text, direct_text, cooldown_seconds FROM rules WHERE media_id = ?", (media_id,))
            else:
                cur.execute("SELECT id, media_id, patterns, reply_text, direct_text, cooldown_seconds FROM rules")
            rows = cur.fetchall()
            out = []
            for r in rows:
                out.append({
                    "id": r[0],
                    "media_id": r[1],
                    "patterns": json.loads(r[2]),
                    "reply_text": r[3],
                    "direct_text": r[4],
                    "cooldown_seconds": r[5]
                })
            return out

    def mark_comment_processed(self, comment_id: str, media_id: str):
        with lock, sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO processed_comments (comment_id, media_id, processed_at) VALUES (?, ?, ?)",
                        (comment_id, media_id, int(time.time())))
            conn.commit()

    def is_comment_processed(self, comment_id: str) -> bool:
        with lock, sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM processed_comments WHERE comment_id = ?", (comment_id,))
            return cur.fetchone() is not None
