# Paper Trading Bot (v15)

Self-contained paper trading app with a desktop GUI and Streamlit dashboard.
- One-click installers via GitHub Actions for Windows (Setup.exe) and Linux (AppImage)
- Auto-updater (checks your GitHub Releases and launches installer)
- Live Decisions "terminal", Settings tab (themes, risk, updates), Learn tab
- Taxes estimator (short/long FIFO) — not tax advice
- Paper-only by default

## Quick start (dev)
```bash
pip install -r requirements.txt
python -m src.db --init
python -m src.paper_trader   # start scheduler in background
streamlit run dashboard/app.py
# or desktop GUI:
python -m gui.launcher
```

## Environment (safe defaults)
Copy `.env.sample` to `.env` to adjust:
```
STRICT_PAPER_ONLY=true
BROKER_MODE=sim_paper
TIMEZONE=America/Chicago

GITHUB_REPO=Syklic/paper-trading-bot
UPDATE_CHANNEL=stable
AUTO_CHECK_UPDATES=true
```

## Build installers (CI)
Push a tag like `v1.5.0`. See `.github/workflows/release.yml`.
