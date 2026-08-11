"""Alert service: acknowledge / assign / resolve / reopen alerts."""

import pandas as pd
import streamlit as st

from services import data_service
from utils.helpers import now_str

SESSION_KEY = "alert_dataframe"


def get_alerts() -> pd.DataFrame:
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = data_service.load_alerts().copy()
    return st.session_state[SESSION_KEY]


def _persist():
    data_service.save_dataframe("alerts", st.session_state[SESSION_KEY])


def _update(alert_id: str, updates: dict) -> bool:
    df = get_alerts()
    mask = df["Alert_ID"] == alert_id
    if not mask.any():
        return False
    for col, val in updates.items():
        df.loc[mask, col] = val
    st.session_state[SESSION_KEY] = df
    _persist()
    return True


def acknowledge(alert_id: str) -> bool:
    return _update(alert_id, {"Status": "Acknowledged"})


def assign(alert_id: str, person: str) -> bool:
    return _update(alert_id, {"Status": "Assigned", "Assigned_Person": person})


def resolve(alert_id: str) -> bool:
    return _update(alert_id, {"Status": "Resolved", "Resolved_Time": now_str()})


def reopen(alert_id: str) -> bool:
    return _update(alert_id, {"Status": "Reopened", "Resolved_Time": ""})


def summary_counts(df: pd.DataFrame = None) -> dict:
    df = df if df is not None else get_alerts()
    if df.empty:
        return {"Information": 0, "Warning": 0, "High": 0, "Critical": 0, "Open": 0}
    open_statuses = ["New", "Acknowledged", "Assigned", "Reopened"]
    return {
        "Information": int((df["Severity"] == "Information").sum()),
        "Warning": int((df["Severity"] == "Warning").sum()),
        "High": int((df["Severity"] == "High").sum()),
        "Critical": int((df["Severity"] == "Critical").sum()),
        "Open": int(df["Status"].isin(open_statuses).sum()),
    }
