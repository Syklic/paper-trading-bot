import pandas as pd
import datetime as dt

def fifo_realized_gains_df(fills_df: pd.DataFrame, year=None):
    if fills_df is None or fills_df.empty:
        return dict(st_gain=0.0, lt_gain=0.0, realized_total=0.0)
    df = fills_df.copy()
    df['ts'] = pd.to_datetime(df['ts'], errors='coerce')
    if year is None:
        year = dt.datetime.now().year
    start = pd.Timestamp(f"{year}-01-01")
    end = pd.Timestamp(f"{year}-12-31 23:59:59")
    df = df[(df['ts'] >= start) & (df['ts'] <= end)]
    if df.empty:
        return dict(st_gain=0.0, lt_gain=0.0, realized_total=0.0)

    realized_st = 0.0
    realized_lt = 0.0
    for sym, g in df.sort_values('ts').groupby('symbol', sort=False):
        inv = []
        for _, row in g.iterrows():
            side = str(row['side']).upper()
            qty = float(row['qty'])
            px = float(row['price'])
            ts = row['ts']
            if side == 'BUY':
                inv.append([qty, px, ts])
            else:
                remaining = qty
                while remaining > 0 and inv:
                    lot_qty, lot_px, lot_ts = inv[0]
                    take = min(lot_qty, remaining)
                    holding_days = (ts - lot_ts).days if pd.notnull(lot_ts) else 0
                    pnl = (px - lot_px) * take
                    if holding_days >= 365:
                        realized_lt += pnl
                    else:
                        realized_st += pnl
                    lot_qty -= take
                    remaining -= take
                    if lot_qty <= 0:
                        inv.pop(0)
                    else:
                        inv[0][0] = lot_qty
    total = realized_st + realized_lt
    return dict(st_gain=realized_st, lt_gain=realized_lt, realized_total=total)

def estimate_tax_liability(st_gain, lt_gain, fed_ord, fed_lt, state, addl=0.0):
    total = st_gain + lt_gain
    tax = st_gain*fed_ord + lt_gain*fed_lt + total*state + total*addl
    return max(tax, 0.0)
