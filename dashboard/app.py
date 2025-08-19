# cSpell:ignore Daytrade daytrade addl selectbox autorefresh dtog dvog mtog maxpos intraday
import os, time, datetime as dt
import pandas as pd
import streamlit as st
from src.db import get_conn, get_all_settings, set_many, log
from src.config import Settings
from src.version import __version__ as APP_VERSION

st.set_page_config(page_title="Paper Trading Bot", layout="wide")

def load_tables():
    with get_conn() as c:
        eq = pd.read_sql_query("SELECT * FROM equity ORDER BY ts", c)
        tr = pd.read_sql_query("SELECT * FROM trades ORDER BY ts DESC", c)
        pos = pd.read_sql_query("SELECT * FROM positions", c)
        fills = pd.read_sql_query("SELECT * FROM fills ORDER BY ts DESC", c)
        rails = pd.read_sql_query("SELECT * FROM bot_log WHERE source='rails' ORDER BY ts DESC", c)
        met = pd.read_sql_query("SELECT * FROM bot_log ORDER BY ts DESC", c)
    return eq, tr, pos, fills, rails, met

def load_settings():
    s = Settings()
    dbs = get_all_settings()
    for k,v in dbs.items():
        if hasattr(s, k):
            try:
                if v in ("True","False"): v = (v=="True")
                else: v = float(v) if "." in v or v.isdigit() else v
            except Exception: pass
            setattr(s,k,v)
    return s

st.title("📈 Paper Trading Bot")
st.caption(f"Version {APP_VERSION} — paper-only safe.")

tab_overview, tab_live, tab_settings, tab_learn = st.tabs(["Overview","Live Decisions","Settings","Learn"])

with tab_overview:
    st.subheader("Status")
    col1,col2,col3,col4,col5,col6 = st.columns(6)
    with col1:
        st.metric("Mode", "Paper")
    with col2:
        s = load_settings()
        st.metric("Daytrade", "On" if s.enable_daytrade else "Off")
    with col3:
        st.metric("Dividend hold", "On" if s.enable_dividend_hold else "Off")
    with col4:
        st.metric("Mimic", "On" if s.enable_mimic_politicians else "Off")
    eq, tr, pos, fills, rails, met = load_tables()

    # Tax snapshot
    st.subheader("Tax snapshot (YTD)")
    try:
        from src.tax import fifo_realized_gains_df, estimate_tax_liability
        if s.tax_enable:
            gains = fifo_realized_gains_df(fills, year=dt.datetime.now().year)
            est_tax = estimate_tax_liability(
                gains['st_gain'], gains['lt_gain'],
                float(s.tax_federal_ord_rate), float(s.tax_federal_lt_rate),
                float(s.tax_state_rate), float(s.tax_addl_rate)
            )
            after_tax = gains['realized_total'] - est_tax
            c1,c2 = st.columns(2)
            c1.metric("Est. tax reserve (YTD)", f"${est_tax:,.0f}")
            c2.metric("After-tax realized (YTD est.)", f"${after_tax:,.0f}")
        else:
            st.caption("Enable in Settings → Taxes to see estimates here.")
    except Exception as e:
        st.caption("Taxes: " + str(e))

    st.subheader("Positions")
    st.dataframe(pos, use_container_width=True, height=200)
    st.subheader("Recent fills")
    st.dataframe(fills.head(50), use_container_width=True, height=240)

with tab_live:
    st.subheader("Live Decisions")

    # controls
    auto = st.toggle("Auto-refresh", True, key="live_auto")
    level = st.selectbox(
        "Level",
        ["all", "info", "debug", "warning", "error"],
        index=0,
        key="live_level"
    )

    # load and filter
    _, _, _, _, _, met = load_tables()
    df = met.copy()
    if level != "all":
        df = df[df["level"] == level]

    # render
    st.dataframe(df.head(200), use_container_width=True, height=500)

    # safe auto-refresh compatible with old/new Streamlit
    if auto:
        time.sleep(2)  # adjust cadence if you want
        try:
            st.rerun()                # Streamlit ≥ 1.30
        except AttributeError:
            st.experimental_rerun()   # older Streamlit


with tab_settings:
    st.subheader("Controls")
    s = load_settings()
    c1,c2,c3 = st.columns(3)
    dtog = c1.toggle("Enable day trading", value=bool(s.enable_daytrade))
    dvog = c2.toggle("Enable dividend holds", value=bool(s.enable_dividend_hold))
    mtog = c3.toggle("Enable mimic politicians", value=bool(s.enable_mimic_politicians))

    st.subheader("Risk")
    r1,r2,r3 = st.columns(3)
    maxpos = r1.number_input("Max position % of equity", value=float(s.max_position_pct)*100.0, min_value=1.0, max_value=100.0, step=1.0)/100.0
    sl = r2.number_input("Per-trade stop loss %", value=float(s.per_trade_stop_loss_pct)*100.0, min_value=0.5, max_value=50.0, step=0.5)/100.0
    dds = r3.number_input("Daily drawdown stop %", value=float(s.daily_drawdown_stop_pct)*100.0, min_value=1.0, max_value=50.0, step=1.0)/100.0

    st.subheader("Appearance")
    a1,a2 = st.columns(2)
    theme = a1.selectbox("Theme", ["dark","light"], index=0 if s.theme=="dark" else 1)
    accent = a2.selectbox("Accent", ["green","blue","purple","orange"], index=0)

    st.subheader("Updates")
    st.caption(f"Repo: {s.github_repo}")
    chan = st.selectbox("Channel", ["stable","prerelease"], index=0 if s.update_channel=="stable" else 1)
    auto_up = st.toggle("Auto-check at launch (GUI only)", value=bool(s.auto_check_updates))
    c1,c2 = st.columns(2)
    with c1:
        if st.button("Check for updates now"):
            try:
                from src.updater import latest_release, compare_versions
                tag, name, asset = latest_release(include_prerelease=(chan=="prerelease"))
                from src.version import __version__ as cur
                if tag is None:
                    st.warning("No releases found.")
                else:
                    cmp = compare_versions(tag, cur)
                    if cmp <= 0:
                        st.success(f"Up to date (current {cur}, latest {tag}).")
                    else:
                        st.warning(f"Update available: {tag} (current {cur}). Use GUI → Check updates to auto-download.")
                        if asset: st.write(f"Suggested asset: {asset.get('name','(no name)')}")
            except Exception as e:
                st.error(str(e))
    with c2:
        st.info("Desktop GUI has a 'Check updates' button that downloads & launches the installer.")

    if st.button("Save settings"):
        set_many({
            "enable_daytrade": bool(dtog),
            "enable_dividend_hold": bool(dvog),
            "enable_mimic_politicians": bool(mtog),
            "max_position_pct": float(maxpos),
            "per_trade_stop_loss_pct": float(sl),
            "daily_drawdown_stop_pct": float(dds),
            "theme": theme,
            "accent": accent,
            "update_channel": chan,
            "auto_check_updates": bool(auto_up)
        })
        st.success("Saved.")

with tab_learn:
    st.subheader("Learn the basics")
    st.markdown("""
- **Day trading**: many small, intraday trades; watch **risk** and **PDT** rules (in real accounts).
- **Long-term/dividends**: compound returns; dividends add cash flow.
- **Paper trading**: practice without real money. This app only simulates until you connect a broker on purpose.
- **Risk**: stop losses, max position size, daily drawdown guard.
- **Crypto vs. stocks**: 24/7 vs. market hours; custody and volatility differ.
""")
