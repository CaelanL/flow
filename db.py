import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flow.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            duration_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def save_transcription(text, duration_ms):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO transcriptions (text, duration_ms) VALUES (?, ?)",
        (text, duration_ms),
    )
    conn.commit()
    conn.close()
