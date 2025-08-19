#!/usr/bin/env bash
set -euo pipefail
NAME=${1:-trading-bot}
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
pyinstaller gui/launcher.py --onefile --noconsole   --name "$NAME"   --add-data "dashboard:dashboard"   --add-data "src:src"   --collect-all streamlit --collect-all plotly --collect-all yfinance --collect-all pandas   --hidden-import sklearn --hidden-import scipy
echo "Binary: dist/$NAME"
