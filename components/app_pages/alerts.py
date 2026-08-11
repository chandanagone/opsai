"""Alerts page: alert summary, filters, detail panel, workflow actions."""

import streamlit as st
import pandas as pd

from components.styles import page_header
from components.notifications import recent_alerts_timeline
from utils.constants import ALERT_CATEGORIES, ALERT_SEVERITIES, ALERT_STATUSES, FACILITIES
from utils.export_utils import df_to_csv_bytes
from services import alert_service


def render(data: dict):
    page_header("Alerts", "Monitor, acknowledge, and resolve operational alerts.")

    df = alert_service.get_alerts()
    counts = alert_service.summary_counts(df)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Information", counts["Information"])
    k2.metric("Warning", counts["Warning"])
    k3.metric("High", counts["High"])
    k4.metric("Critical", counts["Critical"])
    k5.metric("Open", counts["Open"])

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        cat_f = st.multiselect("Category", ALERT_CATEGORIES, key="alert_cat_filter")
    with f2:
        sev_f = st.multiselect("Severity", ALERT_SEVERITIES, key="alert_sev_filter")
    with f3:
        status_f = st.multiselect("Status", ALERT_STATUSES, key="alert_status_filter")
    with f4:
        search = st.text_input("Search title", key="alert_search")

    filtered = df.copy()
    if cat_f:
        filtered = filtered[filtered["Category"].isin(cat_f)]
    if sev_f:
        filtered = filtered[filtered["Severity"].isin(sev_f)]
    if status_f:
        filtered = filtered[filtered["Status"].isin(status_f)]
    if search:
        filtered = filtered[filtered["Alert_Title"].str.contains(search, case=False, na=False)]

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Alert Table</div>", unsafe_allow_html=True)
        if filtered.empty:
            st.info("ℹ️ No alerts match the selected filters.")
        else:
            st.dataframe(
                filtered[["Alert_ID", "Alert_Title", "Category", "Severity", "Facility", "Status", "Created_Time"]],
                use_container_width=True, hide_index=True, height=340,
            )
            st.download_button("⬇️ Export Alerts to CSV", data=df_to_csv_bytes(filtered),
                                file_name="alerts_export.csv", mime="text/csv")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Recent Alert Timeline</div>", unsafe_allow_html=True)
        recent_alerts_timeline(filtered, n=8)
        st.markdown("</div>", unsafe_allow_html=True)

    if not filtered.empty:
        st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Alert Detail & Actions</div>", unsafe_allow_html=True)
        selected_id = st.selectbox("Select Alert", filtered["Alert_ID"].tolist(), key="alert_detail_select")
        row = df[df["Alert_ID"] == selected_id].iloc[0]

        st.write(f"**{row['Alert_Title']}**")
        st.write(row["Description"])
        st.write(f"Category: **{row['Category']}**  |  Severity: **{row['Severity']}**  |  Status: **{row['Status']}**")
        st.write(f"Facility: {row['Facility']}  |  Created: {row['Created_Time']}")

        a1, a2, a3, a4 = st.columns(4)
        with a1:
            if st.button("✅ Acknowledge", key="alert_ack_btn", use_container_width=True):
                alert_service.acknowledge(selected_id)
                st.success("Alert acknowledged.")
                st.rerun()
        with a2:
            assignee = st.text_input("Assign to", key="alert_assign_input", label_visibility="collapsed",
                                      placeholder="Technician name")
            if st.button("👤 Assign", key="alert_assign_btn", use_container_width=True):
                alert_service.assign(selected_id, assignee or "Unassigned")
                st.success("Alert assigned.")
                st.rerun()
        with a3:
            if st.button("🟢 Resolve", key="alert_resolve_btn", use_container_width=True):
                alert_service.resolve(selected_id)
                st.success("Alert resolved.")
                st.rerun()
        with a4:
            if st.button("🔁 Reopen", key="alert_reopen_btn", use_container_width=True):
                alert_service.reopen(selected_id)
                st.success("Alert reopened.")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
