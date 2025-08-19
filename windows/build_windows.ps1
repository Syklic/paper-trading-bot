param(
  [string]$Python="python",
  [string]$Name="TradingBot",
  [switch]$OneFile=$false
)
$ErrorActionPreference="Stop"
& $Python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

$mode = $OneFile.IsPresent ? "--onefile" : "--onedir"
pyinstaller gui\launcher.py $mode --noconsole --name $Name ^
  --icon icons\app-icon.ico ^
  --add-data "dashboard;dashboard" ^
  --add-data "src;src" ^
  --collect-all streamlit --collect-all plotly --collect-all yfinance --collect-all pandas ^
  --hidden-import sklearn --hidden-import scipy

Write-Host "Build complete at dist\$Name"
