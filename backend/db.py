import sqlite3
from pathlib import Path

DB_PATH = Path("rehearsal.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scripts (
            script_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lines (
            line_id TEXT PRIMARY KEY,
            script_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            text TEXT NOT NULL,
            tone TEXT DEFAULT 'neutral',
            ref_audio_path TEXT,
            recording_path TEXT,
            FOREIGN KEY (script_id) REFERENCES scripts(script_id)
        )
    """)
    conn.commit()
    conn.close()