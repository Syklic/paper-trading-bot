import datetime as dt
from ..db import get_conn, log

START_EQUITY = 100_000.0

def _last_equity(c):
    row = c.execute("SELECT equity FROM equity ORDER BY ts DESC LIMIT 1").fetchone()
    return float(row[0]) if row else START_EQUITY

def place_order(symbol: str, side: str, qty: int, price: float):
    side = side.upper()
    assert side in ("BUY", "SELL"), "side must be BUY or SELL"
    assert qty > 0 and price > 0, "qty/price must be positive"

    ts = dt.datetime.utcnow().isoformat()
    notional = qty * float(price)

    with get_conn() as c:
        # record desired trade
        c.execute(
            "INSERT INTO trades(ts,symbol,side,qty,price) VALUES(?,?,?,?,?)",
            (ts, symbol, side, qty, price),
        )
        # paper: immediate fill
        c.execute(
            "INSERT INTO fills(ts,symbol,side,qty,price) VALUES(?,?,?,?,?)",
            (ts, symbol, side, qty, price),
        )

        # positions
        row = c.execute(
            "SELECT qty, avg_price FROM positions WHERE symbol=?", (symbol,)
        ).fetchone()

        if side == "BUY":
            if row:
                oq, ap = int(row[0]), float(row[1])
                new_qty = oq + qty
                new_ap = (oq * ap + qty * price) / new_qty
                c.execute(
                    "UPDATE positions SET qty=?, avg_price=? WHERE symbol=?",
                    (new_qty, new_ap, symbol),
                )
            else:
                c.execute(
                    "INSERT INTO positions(symbol,qty,avg_price) VALUES(?,?,?)",
                    (symbol, qty, price),
                )
        else:  # SELL
            if row:
                oq, ap = int(row[0]), float(row[1])
                new_qty = oq - qty
                if new_qty <= 0:
                    c.execute("DELETE FROM positions WHERE symbol=?", (symbol,))
                else:
                    # avg_price unchanged on partial sell
                    c.execute(
                        "UPDATE positions SET qty=? WHERE symbol=?",
                        (new_qty, symbol),
                    )

        # equity update (simple cash-based model)
        eq0 = _last_equity(c)
        eq1 = eq0 - notional if side == "BUY" else eq0 + notional
        c.execute(
            "INSERT INTO equity(ts,equity) VALUES(?,?)",
            (ts, float(eq1)),
        )

    log("info", "broker", f"Filled {side} {qty} {symbol} @ {price}")

