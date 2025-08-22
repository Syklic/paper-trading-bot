import sqlite3, os
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
        # Equity time series (utc iso timestamps)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS equity(
            ts TEXT NOT NULL,
            equity REAL NOT NULL
        )""")
        # Trades requested
        cur.execute("""
        CREATE TABLE IF NOT EXISTS trades(
            ts TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            qty INTEGER NOT NULL,
            price REAL NOT NULL
        )""")
        # Immediate fills (paper)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS fills(
            ts TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            qty INTEGER NOT NULL,
            price REAL NOT NULL
        )""")
        # Open positions
        cur.execute("""
        CREATE TABLE IF NOT EXISTS positions(
            symbol TEXT PRIMARY KEY,
            qty INTEGER NOT NULL,
            avg_price REAL NOT NULL
        )""")
        # Bot log (audit/rails/metrics)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bot_log(
            ts TEXT NOT NULL,
            level TEXT NOT NULL,
            source TEXT NOT NULL,
            message TEXT NOT NULL
        )""")
        # Settings KV
        cur.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )""")

def log(level, source, message):
    import datetime as dt
    with get_conn() as c:
        c.execute(
            "INSERT INTO bot_log(ts,level,source,message) VALUES(?,?,?,?)",
            (dt.datetime.utcnow().isoformat(), level, source, message),
        )

def set_many(pairs: dict):
    with get_conn() as c:
        for k, v in pairs.items():
            c.execute(
                """
                INSERT INTO settings(key,value) VALUES(?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (k, str(v)),
            )

def get_all_settings():
    with get_conn() as c:
        return {row["key"]: row["value"] for row in c.execute("SELECT key,value FROM settings")}

if __name__ == "__main__":
    init()
    print("DB initialized at", DB_PATH)
