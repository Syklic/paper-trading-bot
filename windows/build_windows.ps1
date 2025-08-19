# cSpell:ignore venv pyinstaller onefile onedir noconsole streamlit plotly yfinance pywebview sklearn scipy iscc Inno
param(
  [string]$Name = "TradingBot",   # set to "PaperBot" if you rebrand
  [switch]$OneFile = $false,      # -OneFile to build a single exe
  [switch]$Installer = $false,    # -Installer to run Inno Setup after build
  [string]$Python = "python"      # path to system python if needed
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# --- Resolve repo root from this script's folder ---
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Resolve-Path (Join-Path $ScriptDir "..")

# --- Create / reuse venv ---
$VenvDir = Join-Path $RepoRoot "venv"
if (!(Test-Path $VenvDir)) {
  & $Python -m venv $VenvDir
}

$Py     = Join-Path $VenvDir "Scripts\python.exe"
$Pip    = Join-Path $VenvDir "Scripts\pip.exe"
$PyInst = Join-Path $VenvDir "Scripts\pyinstaller.exe"

# --- Install deps (pin PyInstaller for stability) ---
& $Py -m pip install --upgrade pip
& $Pip install -r (Join-Path $RepoRoot "requirements.txt")
& $Pip install pyinstaller==6.6.0

# --- Build mode ---
$mode = if ($OneFile) { "--onefile" } else { "--onedir" }

# --- PyInstaller args (array avoids line-continuation issues) ---
$PyArgs = @(
  "gui\launcher.py",
  "--name", $Name,
  $mode,
  "--noconsole",
  "--icon", "icons\app-icon.ico",
  "--add-data", "dashboard;dashboard",
  "--add-data", "src;src",
  "--collect-all", "streamlit",
  "--collect-all", "plotly",
  "--collect-all", "yfinance",
  "--collect-all", "pandas",
  "--collect-all", "pywebview",
  "--hidden-import", "sklearn",
  "--hidden-import", "scipy"
)

Write-Host ">> Building $Name with PyInstaller..."
& $PyInst @PyArgs

$ExePath = Join-Path $RepoRoot "dist\$Name\$Name.exe"
if (!(Test-Path $ExePath)) {
  Write-Error "Expected $ExePath not found. Verify --name matches Inno script and check PyInstaller output."
}

Write-Host ">> Build OK: $ExePath"

# --- Optional installer build ---
if ($Installer) {
  Write-Host ">> Building installer with Inno Setup..."
  if (-not (Get-Command iscc -ErrorAction SilentlyContinue)) {
    choco install innosetup -y
  }
  $IssPath = Join-Path $ScriptDir "TradingBot.iss"
  & iscc $IssPath
  $OutInstaller = Join-Path $ScriptDir "TradingBot-Setup.exe"
  if (!(Test-Path $OutInstaller)) {
    Write-Error "Installer missing at $OutInstaller. Check OutputDir/OutputBaseFilename in $IssPath."
  } else {
    Write-Host ">> Installer OK: $OutInstaller"
  }
}

Write-Host ">> Done."
