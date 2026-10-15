"""
forex_scraper.py
────────────────────────────────────────────────────────────────────────────
Automated forex OHLCV scraper using yfinance + pandas + schedule.

On first launch (double-click / python forex_scraper.py):
  • Prompts the user ONCE for a currency-pair symbol  (e.g. EURUSD, GBPUSD)
  • Immediately runs an initial scrape for all three timeframes
  • Then runs silently on a schedule — no further interaction required

Designed to be placed in the Windows Startup folder and launched via
pythonw.exe for fully silent, background operation after the first run.

Folder layout created automatically:
  <script_dir>/
  ├── forex_scraper.py
  ├── data/
  │   ├── 1H/   <PAIR>.csv
  │   ├── 4H/   <PAIR>.csv
  │   └── 1D/   <PAIR>.csv
  └── logs/
      └── forex_scraper.log
────────────────────────────────────────────────────────────────────────────
Dependencies  (pip install yfinance pandas schedule)
"""

# ── Standard library ────────────────────────────────────────────────────────
import os
import sys
import logging
import time
from datetime import datetime
from pathlib import Path

# ── Third-party ──────────────────────────────────────────────────────────────
try:
    import yfinance as yf
    import pandas as pd
    import schedule
except ImportError as _ie:
    # Surface import errors even when running under pythonw.exe
    import ctypes
    ctypes.windll.user32.MessageBoxW(
        0,
        f"Missing dependency — run:\n  pip install yfinance pandas schedule\n\nDetail: {_ie}",
        "forex_scraper — import error",
        0x10,
    )
    sys.exit(1)


# ════════════════════════════════════════════════════════════════════════════
#  PATHS & CONSTANTS
# ════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR   = SCRIPT_DIR / "data"
LOG_DIR    = SCRIPT_DIR / "logs"

TIMEFRAMES = {
    "1H": {"yf_interval": "1h",  "yf_period": "7d",   "resample": None},
    "4H": {"yf_interval": "1h",  "yf_period": "60d",  "resample": "4h"},
    "1D": {"yf_interval": "1d",  "yf_period": "2y",   "resample": None},
}

SCHEDULE_HOURS = {"1H": 1, "4H": 4, "1D": 24}

# Columns written to / expected from disk
OHLCV_COLS = ["Datetime", "Open", "High", "Low", "Close", "Volume"]


# ════════════════════════════════════════════════════════════════════════════
#  LOGGING SETUP
# ════════════════════════════════════════════════════════════════════════════

def setup_logging() -> logging.Logger:
    """Configure rotating-friendly file logger + optional stderr handler."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "forex_scraper.log"

    fmt = "%(asctime)s  %(levelname)-8s  %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        datefmt=datefmt,
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            # Only attach a StreamHandler when running in a real console
            *([] if not sys.stdout or not sys.stdout.isatty()
              else [logging.StreamHandler(sys.stdout)]),
        ],
    )
    return logging.getLogger("forex_scraper")


logger = setup_logging()


# ════════════════════════════════════════════════════════════════════════════
#  HELPER — notify on Windows (works under pythonw.exe too)
# ════════════════════════════════════════════════════════════════════════════

def _win_notify(title: str, message: str) -> None:
    """Non-blocking Windows MessageBox — used only for startup/fatal messages."""
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, 0)
    except Exception:
        pass  # Non-Windows or ctypes unavailable — silently skip


# ════════════════════════════════════════════════════════════════════════════
#  USER INPUT — currency-pair symbol (runs ONCE at startup)
# ════════════════════════════════════════════════════════════════════════════

def prompt_for_symbol() -> str:
    """
    Ask the user for a forex pair symbol.
    Runs once on launch; cleans and validates the input.

    Returns a normalised upper-case ticker, e.g. 'EURUSD'.
    """
    while True:
        raw = input(
            "\n┌─────────────────────────────────────────────┐\n"
            "│  Forex Scraper — Pair Setup                 │\n"
            "└─────────────────────────────────────────────┘\n"
            "  Enter the currency-pair symbol to track\n"
            "  Examples: EURUSD  GBPUSD  USDJPY  AUDUSD\n\n"
            "  Symbol ❯ "
        ).strip().upper()

        # Strip any accidental suffix the user may have typed
        clean = raw.replace("=X", "").replace("/", "").replace("-", "")

        if len(clean) < 6:
            print(f"  ✗  '{raw}' looks too short.  Please enter a 6-character pair (e.g. EURUSD).\n")
            continue

        # Quick sanity-check: does yfinance know this ticker?
        print(f"\n  Verifying '{clean}' with Yahoo Finance …", end="", flush=True)
        try:
            info = yf.Ticker(f"{clean}=X").fast_info
            # fast_info raises / returns empty-ish dict for unknown tickers
            last_price = getattr(info, "last_price", None)
            if last_price is None or last_price == 0.0:
                raise ValueError("No price data returned")
            print(f"  ✓  Found (last price ≈ {last_price:.5f})\n")
            return clean
        except Exception as e:
            print(f"\n  ✗  Could not verify '{clean}': {e}")
            retry = input("  Try a different symbol? [Y/n] ❯ ").strip().lower()
            if retry in ("n", "no"):
                # Allow proceeding even if verification failed (offline / rate-limited)
                print(f"  ⚠  Proceeding with '{clean}' unverified.\n")
                return clean


# ════════════════════════════════════════════════════════════════════════════
#  CORE — fetch, resample, deduplicate, persist
# ════════════════════════════════════════════════════════════════════════════

def _fetch_raw(yf_ticker: str, interval: str, period: str) -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance and normalise the DataFrame."""
    ticker = yf.Ticker(yf_ticker)
    df = ticker.history(interval=interval, period=period, auto_adjust=True)

    if df.empty:
        raise ValueError(f"yfinance returned empty data for {yf_ticker} [{interval}/{period}]")

    df.index = df.index.tz_localize(None)          # drop timezone → naive UTC
    df.index.name = "Datetime"
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.reset_index(inplace=True)
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    return df


def _resample_4h(df_1h: pd.DataFrame) -> pd.DataFrame:
    """Aggregate 1H candles into 4H OHLCV candles."""
    df = df_1h.set_index("Datetime").sort_index()
    resampled = df.resample("4h", label="left", closed="left").agg(
        Open=("Open",   "first"),
        High=("High",   "max"),
        Low=("Low",    "min"),
        Close=("Close",  "last"),
        Volume=("Volume", "sum"),
    ).dropna(subset=["Open", "Close"])
    resampled.reset_index(inplace=True)
    return resampled


def _load_existing(csv_path: Path) -> pd.DataFrame:
    """Read an existing CSV; return empty DataFrame if file absent or corrupt."""
    if not csv_path.exists():
        return pd.DataFrame(columns=OHLCV_COLS)
    try:
        df = pd.read_csv(csv_path, parse_dates=["Datetime"])
        return df
    except Exception as e:
        logger.warning("Could not read %s (%s) — treating as empty.", csv_path, e)
        return pd.DataFrame(columns=OHLCV_COLS)


def _append_and_dedup(csv_path: Path, new_df: pd.DataFrame) -> int:
    """
    Merge new_df with whatever is already in csv_path.
    Deduplication is by Datetime.
    Returns the number of genuinely new rows appended.
    """
    existing = _load_existing(csv_path)
    combined = pd.concat([existing, new_df], ignore_index=True)
    combined["Datetime"] = pd.to_datetime(combined["Datetime"])
    before = len(combined)
    combined.drop_duplicates(subset=["Datetime"], keep="last", inplace=True)
    combined.sort_values("Datetime", inplace=True)
    combined.reset_index(drop=True, inplace=True)
    new_rows = len(combined) - len(existing)

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(csv_path, index=False, date_format="%Y-%m-%d %H:%M:%S")
    return max(new_rows, 0)


# ════════════════════════════════════════════════════════════════════════════
#  SCRAPE JOBS — one per timeframe
# ════════════════════════════════════════════════════════════════════════════

def scrape_timeframe(pair: str, tf: str) -> None:
    """
    Fetch, (optionally resample), deduplicate, and persist data for one
    timeframe.  Errors are logged but never re-raised — the scheduler keeps
    running.
    """
    cfg       = TIMEFRAMES[tf]
    yf_ticker = f"{pair}=X"
    csv_path  = DATA_DIR / tf / f"{pair}.csv"

    try:
        df_raw = _fetch_raw(yf_ticker, cfg["yf_interval"], cfg["yf_period"])

        if cfg["resample"] == "4h":
            df_out = _resample_4h(df_raw)
        else:
            df_out = df_raw

        added = _append_and_dedup(csv_path, df_out)
        logger.info("[%s | %s]  Scraped %d rows  →  %d new appended  →  %s",
                    pair, tf, len(df_out), added, csv_path)

    except Exception as exc:
        logger.error("[%s | %s]  Scrape failed: %s", pair, tf, exc, exc_info=True)


def make_job(pair: str, tf: str):
    """Return a zero-argument callable suitable for schedule."""
    def _job():
        scrape_timeframe(pair, tf)
    _job.__name__ = f"scrape_{pair}_{tf}"
    return _job


# ════════════════════════════════════════════════════════════════════════════
#  SCHEDULER SETUP
# ════════════════════════════════════════════════════════════════════════════

def register_schedules(pair: str) -> None:
    """
    Register recurring jobs.
    1H  → every 1 hour
    4H  → every 4 hours
    1D  → every 24 hours (at the top of the next full hour boundary)
    """
    schedule.every(SCHEDULE_HOURS["1H"]).hours.do(make_job(pair, "1H"))
    schedule.every(SCHEDULE_HOURS["4H"]).hours.do(make_job(pair, "4H"))
    schedule.every(SCHEDULE_HOURS["1D"]).hours.do(make_job(pair, "1D"))

    logger.info("Scheduled  %s  →  1H every 1 h | 4H every 4 h | 1D every 24 h", pair)


# ════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # ── 1. Greet & collect symbol ────────────────────────────────────────────
    pair = prompt_for_symbol()

    # ── 2. Ensure directory tree exists ─────────────────────────────────────
    for tf in TIMEFRAMES:
        (DATA_DIR / tf).mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("══════════════════════════════════════════════════════")
    logger.info("  Forex Scraper started  |  Pair: %s  |  %s", pair,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("══════════════════════════════════════════════════════")

    # ── 3. Immediate initial scrape for all timeframes ───────────────────────
    print(f"\n  Running initial scrape for {pair} across 1H / 4H / 1D …\n")
    for tf in TIMEFRAMES:
        scrape_timeframe(pair, tf)
        csv_path = DATA_DIR / tf / f"{pair}.csv"
        if csv_path.exists():
            row_count = sum(1 for _ in open(csv_path)) - 1  # subtract header
            print(f"  ✓  {tf}  →  {csv_path.relative_to(SCRIPT_DIR)}  "
                  f"({row_count} rows total)")
        else:
            print(f"  ✗  {tf}  →  No data written (check logs)")

    # ── 4. Register recurring schedule ──────────────────────────────────────
    register_schedules(pair)

    # ── 5. Startup confirmation (visible in console + log) ───────────────────
    success_msg = (
        f"Script has been executed successfully\n\n"
        f"Pair   : {pair}\n"
        f"Data   : {DATA_DIR}\n"
        f"Logs   : {LOG_DIR / 'forex_scraper.log'}\n\n"
        f"Schedule\n"
        f"  1H  →  every 1 hour\n"
        f"  4H  →  every 4 hours\n"
        f"  1D  →  every 24 hours\n\n"
        f"The script is now running silently in the background."
    )
    logger.info("Script has been executed successfully  (pair=%s)", pair)
    print(f"\n{'─'*55}")
    print(success_msg)
    print(f"{'─'*55}\n")
    print("  The scraper is now running.  You can close this window —")
    print("  or leave it open to watch log output.\n")

    # ── 6. Main loop — run pending jobs, catch & log any stray exceptions ───
    while True:
        try:
            schedule.run_pending()
        except Exception as loop_exc:
            error_msg = f"Script has run into an error: {loop_exc}"
            logger.error(error_msg, exc_info=True)
        time.sleep(30)   # poll every 30 s — lightweight on CPU


# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scraper stopped by user (KeyboardInterrupt).")
        print("\n  Scraper stopped.  Goodbye.\n")
        sys.exit(0)
    except Exception as fatal:
        msg = f"Script has run into an error: {fatal}"
        logger.critical(msg, exc_info=True)
        _win_notify("forex_scraper — Fatal Error", msg)
        sys.exit(1)
