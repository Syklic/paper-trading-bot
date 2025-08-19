import random, datetime as dt
from .broker.paper import place_order
from .db import log

WATCH = ["AAPL","MSFT","NVDA","SPY","QQQ","BTC-USD","ETH-USD"]

def daytrade_tick():
    sym = random.choice(WATCH)
    side = random.choice(["BUY","SELL"])
    qty = random.choice([1,2,3,5])
    price = round(random.uniform(50, 500), 2)
    place_order(sym, side, qty, price)
    log("debug","daytrade", f"Simulated {side} {qty} {sym} @ {price}")

def dividend_hold_tick():
    # placeholder: pretend we buy dividend stocks periodically
    sym = random.choice(["KO","PEP","JNJ","PG","T","VZ"])
    qty = 1
    price = round(random.uniform(30, 200),2)
    place_order(sym, "BUY", qty, price)
    log("info","dividend","Accumulating {}".format(sym))

def mimic_politicians_tick():
    # placeholder: follow a fake Pelosi trade feed (mock)
    sym = random.choice(["MSFT","NVDA","CRM","PANW"])
    qty = 1
    price = round(random.uniform(100, 700),2)
    place_order(sym, "BUY", qty, price)
    log("info","mimic","Mimic buy {} from politician feed".format(sym))
