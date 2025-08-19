import sqlite3, os, time
from contextlib import contextmanager

DB_PATH = os.getenv("DB_PATH", "paper.db")

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init():
    with get_conn() as c:
        cur = c.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS equity(
            ts TEXT PRIMARY KEY,
            equity REAL
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS trades(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            symbol TEXT,
            side TEXT,
            qty REAL,
            price REAL
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS fills(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            symbol TEXT,
            side TEXT,
            qty REAL,
            price REAL,
            commission REAL DEFAULT 0.0
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS positions(
            symbol TEXT PRIMARY KEY,
            qty REAL,
            avg_price REAL
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS bot_log(
            ts TEXT,
            level TEXT,
            source TEXT,
            message TEXT
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )""")

def log(level, source, message):
    import datetime as dt
    with get_conn() as c:
        c.execute("INSERT INTO bot_log(ts,level,source,message) VALUES(?,?,?,?)",
                  (dt.datetime.utcnow().isoformat(), level, source, message))

def set_many(pairs: dict):
    with get_conn() as c:
        for k,v in pairs.items():
            c.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (k, str(v)))

def get_all_settings():
    with get_conn() as c:
        return {row[0]: row[1] for row in c.execute("SELECT key,value FROM settings")}

if __name__ == "__main__":
    init()
    print("DB initialized at", DB_PATH)
