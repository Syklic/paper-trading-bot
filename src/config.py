import os
from pydantic import BaseModel

class Settings(BaseModel):
    # Mode & safety
    strict_paper_only: bool = (os.getenv("STRICT_PAPER_ONLY", "true").lower()=="true")
    broker_mode: str = os.getenv("BROKER_MODE", "sim_paper")  # sim_paper | alpaca_paper (future)

    # Strategy toggles
    enable_daytrade: bool = True
    enable_dividend_hold: bool = True
    enable_mimic_politicians: bool = False

    # Risk controls
    max_position_pct: float = 0.1
    per_trade_stop_loss_pct: float = 0.02
    daily_drawdown_stop_pct: float = 0.05

    # UI/appearance
    theme: str = os.getenv("THEME", "dark")
    accent: str = os.getenv("ACCENT", "green")

    # Updates
    github_repo: str = os.getenv("GITHUB_REPO", "Syklic/paper-trading-bot")
    update_channel: str = os.getenv("UPDATE_CHANNEL", "stable")  # stable | prerelease
    auto_check_updates: bool = (os.getenv("AUTO_CHECK_UPDATES","true").lower()=="true")

    # Taxes (estimator)
    tax_enable: bool = (os.getenv("TAX_ENABLE", "false").lower() == "true")
    tax_federal_ord_rate: float = float(os.getenv("TAX_FEDERAL_ORD_RATE", "0.22"))
    tax_federal_lt_rate: float = float(os.getenv("TAX_FEDERAL_LT_RATE", "0.15"))
    tax_state_rate: float = float(os.getenv("TAX_STATE_RATE", "0.05"))
    tax_addl_rate: float = float(os.getenv("TAX_ADDL_RATE", "0.00"))
