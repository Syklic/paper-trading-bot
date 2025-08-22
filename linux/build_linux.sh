#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller==6.6.0

pyinstaller gui/launcher.py --name TradingBot --onedir --noconsole \
  --add-data "dashboard:dashboard" \
  --add-data "src:src" \
  --collect-all streamlit \
  --collect-all plotly \
  --collect-all yfinance \
  --collect-all pandas \
  --hidden-import sklearn \
  --hidden-import scipy

echo "Built. See dist/TradingBot"
