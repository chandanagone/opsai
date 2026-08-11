"""Asset service: CRUD operations for facility assets."""

import pandas as pd
import streamlit as st

from services import data_service
from utils.helpers import generate_id, today_str

SESSION_KEY = "asset_dataframe"


def get_assets() -> pd.DataFrame:
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = data_service.load_assets().copy()
    return st.session_state[SESSION_KEY]


def _persist():
    data_service.save_dataframe("assets", st.session_state[SESSION_KEY])


def create_asset(record: dict) -> str:
    df = get_assets()
    new_id = generate_id("AST", df["Asset_ID"].tolist() if not df.empty else [], width=4)
    record["Asset_ID"] = new_id
    record.setdefault("Installation_Date", today_str())
    record.setdefault("Last_Maintenance_Date", today_str())
    new_row = pd.DataFrame([record])
    st.session_state[SESSION_KEY] = pd.concat([df, new_row], ignore_index=True)
    _persist()
    return new_id


def update_asset(asset_id: str, updates: dict) -> bool:
    df = get_assets()
    mask = df["Asset_ID"] == asset_id
    if not mask.any():
        return False
    for col, val in updates.items():
        df.loc[mask, col] = val
    st.session_state[SESSION_KEY] = df
    _persist()
    return True


def delete_asset(asset_id: str) -> bool:
    df = get_assets()
    mask = df["Asset_ID"] == asset_id
    if not mask.any():
        return False
    st.session_state[SESSION_KEY] = df.loc[~mask].reset_index(drop=True)
    _persist()
    return True


def get_asset_work_orders(asset_id: str, work_orders_df: pd.DataFrame) -> pd.DataFrame:
    if work_orders_df is None or work_orders_df.empty:
        return pd.DataFrame()
    return work_orders_df[work_orders_df["Asset_ID"] == asset_id]


def get_asset_maintenance_history(asset_id: str, maint_df: pd.DataFrame) -> pd.DataFrame:
    if maint_df is None or maint_df.empty:
        return pd.DataFrame()
    return maint_df[maint_df["Asset_ID"] == asset_id]


def upcoming_maintenance(df: pd.DataFrame = None, days_ahead: int = 30) -> pd.DataFrame:
    df = df if df is not None else get_assets()
    if df.empty:
        return df
    today = pd.Timestamp(today_str())
    next_maint = pd.to_datetime(df["Next_Maintenance_Date"], errors="coerce")
    horizon = today + pd.Timedelta(days=days_ahead)
    return df[(next_maint >= today) & (next_maint <= horizon)]
