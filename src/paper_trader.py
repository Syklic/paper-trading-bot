import time, datetime as dt, threading
from .db import init, log
from .config import Settings
from . import strategies

RUN = True

def loop():
    s = Settings()
    log("info", "scheduler", f"Starting scheduler (paper-only={s.strict_paper_only})")
    while RUN:
        try:
            # reload toggles each cycle (in case user changes Settings)
            s = Settings()
            if s.enable_daytrade:
                strategies.daytrade_tick()
            if s.enable_dividend_hold and dt.datetime.utcnow().second % 15 == 0:
                strategies.dividend_hold_tick()
            if s.enable_mimic_politicians and dt.datetime.utcnow().second % 20 == 0:
                strategies.mimic_politicians_tick()
            time.sleep(2)
        except Exception as e:
            log("error", "scheduler", str(e))
            time.sleep(2)

def main():
    init()
    t = threading.Thread(target=loop, daemon=True)
    t.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        global RUN
        RUN = False
        log("warning", "scheduler", "Stop requested")

if __name__ == "__main__":
    main()

