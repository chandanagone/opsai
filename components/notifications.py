"""Small notification/alert-strip helpers used across pages."""

import streamlit as st
import pandas as pd


def alert_summary_strip(alerts_df: pd.DataFrame):
    if alerts_df is None or alerts_df.empty:
        st.success("✅ No active alerts at this time.")
        return
    open_statuses = ["New", "Acknowledged", "Assigned", "Reopened"]
    open_alerts = alerts_df[alerts_df["Status"].isin(open_statuses)]
    critical = open_alerts[open_alerts["Severity"] == "Critical"]
    if not critical.empty:
        st.error(f"🚨 {len(critical)} critical alert(s) require immediate attention.")
    elif not open_alerts.empty:
        st.warning(f"⚠️ {len(open_alerts)} open alert(s) awaiting review.")
    else:
        st.success("✅ All alerts resolved.")


def recent_alerts_timeline(alerts_df: pd.DataFrame, n: int = 5):
    if alerts_df is None or alerts_df.empty:
        st.info("ℹ️ No recent alerts.")
        return
    recent = alerts_df.sort_values("Created_Time", ascending=False).head(n)
    icon_map = {"Critical": "🔴", "High": "🟠", "Warning": "🟡", "Information": "🔵"}
    for _, row in recent.iterrows():
        icon = icon_map.get(row.get("Severity", ""), "⚪")
        st.markdown(
            f"{icon} **{row.get('Alert_Title','')}** — {row.get('Facility','')} "
            f"<span style='color:#94a3b8;font-size:12px;'>({row.get('Created_Time','')})</span>",
            unsafe_allow_html=True,
        )
