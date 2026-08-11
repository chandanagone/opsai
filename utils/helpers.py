"""Generic helper functions used throughout the enhanced application."""

from datetime import datetime, date
import random
import string

import pandas as pd

from utils import constants as C


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def generate_id(prefix: str, existing_ids=None, width: int = 4) -> str:
    """Generate a new unique-ish sequential-looking ID such as WO-00033."""
    existing_ids = existing_ids or []
    nums = []
    for i in existing_ids:
        try:
            nums.append(int(str(i).split("-")[-1]))
        except (ValueError, IndexError):
            continue
    next_num = (max(nums) + 1) if nums else 1
    return f"{prefix}-{next_num:0{width}d}"


def random_suffix(n: int = 4) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


def safe_mean(series, default=0.0):
    try:
        if series is None or len(series) == 0:
            return default
        val = pd.to_numeric(series, errors="coerce").mean()
        return default if pd.isna(val) else round(float(val), 2)
    except Exception:
        return default


def safe_sum(series, default=0.0):
    try:
        if series is None or len(series) == 0:
            return default
        val = pd.to_numeric(series, errors="coerce").sum()
        return default if pd.isna(val) else round(float(val), 2)
    except Exception:
        return default


def badge_html(text: str, color: str, text_color: str = "#ffffff") -> str:
    """Return an HTML pill/badge snippet for a status/priority/severity value."""
    return (
        f"<span style='background-color:{color}; color:{text_color}; "
        f"padding:3px 10px; border-radius:999px; font-size:12px; "
        f"font-weight:600; white-space:nowrap;'>{text}</span>"
    )


def status_badge(value: str) -> str:
    color = C.STATUS_COLOR_MAP.get(value, C.COLOR_MUTED)
    return badge_html(value, color)


def priority_badge(value: str) -> str:
    color = C.PRIORITY_COLOR_MAP.get(value, C.COLOR_MUTED)
    return badge_html(value, color)


def severity_badge(value: str) -> str:
    color = C.SEVERITY_COLOR_MAP.get(value, C.COLOR_MUTED)
    return badge_html(value, color)


def format_currency(value, symbol: str = "₹") -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return f"{symbol}0"
    if abs(value) >= 100000:
        return f"{symbol}{value/100000:.2f}L"
    if abs(value) >= 1000:
        return f"{symbol}{value/1000:.1f}K"
    return f"{symbol}{value:,.0f}"


def format_number(value, suffix: str = "") -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "0"
    if value == int(value):
        return f"{int(value):,}{suffix}"
    return f"{value:,.1f}{suffix}"


def parse_date_safe(value, default=None):
    if value is None or value == "" or (isinstance(value, float) and pd.isna(value)):
        return default
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return default


def clamp(value, low, high):
    return max(low, min(high, value))


def empty_state(message: str = "No data available yet."):
    import streamlit as st
    st.info(f"ℹ️ {message}")
