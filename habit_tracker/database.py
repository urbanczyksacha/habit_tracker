import sqlite3
from contextlib import contextmanager

DB_PATH = "habit_tracker.db"

@contextmanager
def db_conn():
    conn = sqlite3.connect(DB_PATH)
    #conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()