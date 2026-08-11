"""
data_service.py
----------------
Central place for loading and (where needed) persisting CSV-backed data for
the enhanced application. Always reads the original facility_data.csv
read-only, and manages the new /data folder files, regenerating them safely
if they are missing, empty, or corrupted.
"""

import os
import pandas as pd
import streamlit as st

import generate_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ORIGINAL_CSV = os.path.join(BASE_DIR, "facility_data.csv")

FILES = {
    "work_orders": "work_orders.csv",
    "assets": "assets.csv",
    "alerts": "alerts.csv",
    "users": "users.csv",
    "energy_history": "energy_history.csv",
    "maintenance_history": "maintenance_history.csv",
    "integrations": "integrations.csv",
}


def _safe_read_csv(path: str, regenerate_key: str = None) -> pd.DataFrame:
    try:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            raise FileNotFoundError
        df = pd.read_csv(path)
        if df.empty:
            raise ValueError("Empty dataframe")
        return df
    except Exception:
        # Attempt regeneration of the entire data directory as a safe fallback
        try:
            generate_data.generate_all(force=True)
            if os.path.exists(path):
                return pd.read_csv(path)
        except Exception:
            pass
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_original_facility_data() -> pd.DataFrame:
    """Read-only load of the ORIGINAL facility_data.csv. Never modified."""
    try:
        df = pd.read_csv(ORIGINAL_CSV)
        if df.empty:
            raise ValueError
        return df
    except Exception:
        return pd.DataFrame({
            'Day': [1, 2, 3, 4, 5],
            'Energy_Usage_kWh': [120, 110, 130, 125, 140],
            'Work_Orders_Closed': [5, 3, 7, 4, 6],
            'Space_Utilization_Pct': [80, 75, 85, 82, 90],
            'Security_Events': [1, 0, 2, 0, 1]
        })


def _path(key: str) -> str:
    return os.path.join(DATA_DIR, FILES[key])


@st.cache_data(show_spinner=False)
def load_work_orders() -> pd.DataFrame:
    return _safe_read_csv(_path("work_orders"))


@st.cache_data(show_spinner=False)
def load_assets() -> pd.DataFrame:
    return _safe_read_csv(_path("assets"))


@st.cache_data(show_spinner=False)
def load_alerts() -> pd.DataFrame:
    return _safe_read_csv(_path("alerts"))


@st.cache_data(show_spinner=False)
def load_users() -> pd.DataFrame:
    return _safe_read_csv(_path("users"))


@st.cache_data(show_spinner=False)
def load_energy_history() -> pd.DataFrame:
    return _safe_read_csv(_path("energy_history"))


@st.cache_data(show_spinner=False)
def load_maintenance_history() -> pd.DataFrame:
    return _safe_read_csv(_path("maintenance_history"))


@st.cache_data(show_spinner=False)
def load_integrations() -> pd.DataFrame:
    return _safe_read_csv(_path("integrations"))


def save_dataframe(key: str, df: pd.DataFrame) -> bool:
    """Persist a dataframe back to its CSV file and clear the relevant cache."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_csv(_path(key), index=False)
        clear_cache()
        return True
    except Exception as exc:
        st.error(f"⚠️ Could not save data ({key}): {exc}")
        return False


def clear_cache():
    """Clear cached data reads after a write operation."""
    for fn in [
        load_work_orders, load_assets, load_alerts, load_users,
        load_energy_history, load_maintenance_history, load_integrations,
    ]:
        try:
            fn.clear()
        except Exception:
            pass


def ensure_data_ready():
    """Called at app startup to guarantee /data exists with valid content."""
    os.makedirs(DATA_DIR, exist_ok=True)
    missing_or_empty = False
    for fname in FILES.values():
        p = os.path.join(DATA_DIR, fname)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            missing_or_empty = True
            break
    if missing_or_empty:
        try:
            generate_data.generate_all(force=False)
        except Exception as exc:
            st.warning(f"Could not auto-generate sample data: {exc}")
