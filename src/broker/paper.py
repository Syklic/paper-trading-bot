import random, datetime as dt
from ..db import get_conn, log

def get_cash_equity():
    with get_conn() as c:
        # approximate equity from starting 100k + PnL
        rows = list(c.execute("SELECT equity FROM equity ORDER BY ts DESC LIMIT 1"))
        if rows:
            return rows[0][0]
        return 100000.0

def place_order(symbol, side, qty, price):
    ts = dt.datetime.utcnow().isoformat()
    with get_conn() as c:
        c.execute("INSERT INTO trades(ts,symbol,side,qty,price) VALUES(?,?,?,?,?)", (ts, symbol, side, qty, price))
        # naive: immediate fill at same price
        c.execute("INSERT INTO fills(ts,symbol,side,qty,price,commission) VALUES(?,?,?,?,?,?)", (ts, symbol, side, qty, price, 0.0))
        # update position
        # simple avg price calc
        row = c.execute("SELECT qty, avg_price FROM positions WHERE symbol=?", (symbol,)).fetchone()
        if side.upper() == "BUY":
            if row:
                oq, ap = row
                new_qty = oq + qty
                new_ap = (oq*ap + qty*price)/new_qty
                c.execute("UPDATE positions SET qty=?, avg_price=? WHERE symbol=?", (new_qty, new_ap, symbol))
            else:
                c.execute("INSERT INTO positions(symbol,qty,avg_price) VALUES(?,?,?)", (symbol, qty, price))
        else:
            if row:
                oq, ap = row
                new_qty = oq - qty
                if new_qty <= 0:
                    c.execute("DELETE FROM positions WHERE symbol=?", (symbol,))
                else:
                    c.execute("UPDATE positions SET qty=? WHERE symbol=?", (new_qty, symbol))
    log("info","broker","Filled {} {} {} @ {}".format(side, qty, symbol, price))
