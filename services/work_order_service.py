"""Work order service: CRUD operations layered on top of data_service."""

import pandas as pd
import streamlit as st

from services import data_service
from utils.helpers import generate_id, now_str, today_str

SESSION_KEY = "wo_dataframe"


def get_work_orders() -> pd.DataFrame:
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = data_service.load_work_orders().copy()
    return st.session_state[SESSION_KEY]


def _persist():
    data_service.save_dataframe("work_orders", st.session_state[SESSION_KEY])


def create_work_order(record: dict) -> str:
    df = get_work_orders()
    new_id = generate_id("WO", df["Work_Order_ID"].tolist() if not df.empty else [], width=5)
    record["Work_Order_ID"] = new_id
    record.setdefault("Created_Date", today_str())
    record.setdefault("Completion_Date", "")
    record.setdefault("Actual_Cost", 0.0)
    new_row = pd.DataFrame([record])
    st.session_state[SESSION_KEY] = pd.concat([df, new_row], ignore_index=True)
    _persist()
    return new_id


def update_work_order(work_order_id: str, updates: dict) -> bool:
    df = get_work_orders()
    mask = df["Work_Order_ID"] == work_order_id
    if not mask.any():
        return False
    for col, val in updates.items():
        df.loc[mask, col] = val
    st.session_state[SESSION_KEY] = df
    _persist()
    return True


def delete_work_order(work_order_id: str) -> bool:
    df = get_work_orders()
    mask = df["Work_Order_ID"] == work_order_id
    if not mask.any():
        return False
    st.session_state[SESSION_KEY] = df.loc[~mask].reset_index(drop=True)
    _persist()
    return True


def change_status(work_order_id: str, new_status: str) -> bool:
    updates = {"Status": new_status}
    if new_status == "Completed":
        updates["Completion_Date"] = today_str()
    return update_work_order(work_order_id, updates)


def assign_technician(work_order_id: str, technician: str) -> bool:
    return update_work_order(work_order_id, {"Assigned_Technician": technician, "Status": "Assigned"})


def get_overdue(df: pd.DataFrame = None) -> pd.DataFrame:
    df = df if df is not None else get_work_orders()
    if df.empty:
        return df
    today = pd.Timestamp(today_str())
    due = pd.to_datetime(df["Due_Date"], errors="coerce")
    open_statuses = ["Open", "Assigned", "In Progress", "On Hold"]
    return df[(due < today) & (df["Status"].isin(open_statuses))]
