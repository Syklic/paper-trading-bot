param(
  [switch]$OneFile = $false
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller==6.6.0

$common = @(
  "gui\launcher.py",
  "--name","TradingBot",
  "--noconsole"
)
if ($OneFile) {
  $common += "--onefile"
} else {
  $common += "--onedir"
}
$args = $common + @(
  "--add-data","dashboard;dashboard",
  "--add-data","src;src",
  "--collect-all","streamlit",
  "--collect-all","plotly",
  "--collect-all","yfinance",
  "--collect-all","pandas",
  "--hidden-import","sklearn",
  "--hidden-import","scipy"
)
pyinstaller @args
Write-Host "Built. See dist\TradingBot"
