import sqlite3
from contextlib import contextmanager

DB_PATH = ".\database\habit_tracker.db"
@contextmanager
def db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_database():
    with db_conn() as conn:
        cursor = conn.cursor()
        with open("schema.sql", "r") as f:
            schema = f.read()
    
        cursor.executescript(schema)
    