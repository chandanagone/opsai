"""Reports page: select, preview, generate, and download reports."""

import streamlit as st
from datetime import timedelta
import pandas as pd

from components.styles import page_header
from utils.constants import FACILITIES
from utils.export_utils import df_to_csv_bytes
from services import report_service


def render(data: dict):
    page_header("Reports", "Generate, preview, and download operational reports.")

    cols = st.columns(3)
    for idx, r in enumerate(report_service.REPORT_TYPES):
        with cols[idx % 3]:
            st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='ops-card-title'>📄 {r}</div>", unsafe_allow_html=True)
            st.caption("Ready to generate")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
    st.markdown("<div class='ops-card-title'>Generate a Report</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        report_type = st.selectbox("Report", report_service.REPORT_TYPES, key="rep_type")
    with c2:
        facility = st.selectbox("Facility", ["All Facilities"] + FACILITIES, key="rep_facility")
    with c3:
        date_range = st.date_input(
            "Date range",
            value=(pd.Timestamp.now().date() - timedelta(days=30), pd.Timestamp.now().date()),
            key="rep_dates",
        )
    date_label = f"{date_range[0]} to {date_range[1]}" if isinstance(date_range, tuple) and len(date_range) == 2 else "All time"

    b1, b2 = st.columns(2)
    with b1:
        preview_clicked = st.button("👁️ Preview Report", use_container_width=True, key="rep_preview_btn")
    with b2:
        generate_clicked = st.button("📥 Generate Report", use_container_width=True, key="rep_generate_btn")

    if preview_clicked or generate_clicked:
        wo = data["work_orders"] if facility == "All Facilities" else data["work_orders"][data["work_orders"]["Facility"] == facility]
        assets = data["assets"] if facility == "All Facilities" else data["assets"][data["assets"]["Facility"] == facility]
        alerts = data["alerts"] if facility == "All Facilities" else data["alerts"][data["alerts"]["Facility"] == facility]
        energy = data["energy_history"] if facility == "All Facilities" else data["energy_history"][data["energy_history"]["Facility"] == facility]

        html = report_service.build_report(
            report_type, facility, date_label,
            work_orders=wo, assets=assets, alerts=alerts, energy=energy,
            maintenance=data["maintenance_history"], users=data["users"],
            original_metrics=data["original_metrics"],
        )
        st.session_state["rep_last_html"] = html
        st.session_state["rep_last_type"] = report_type

        st.components.v1.html(html, height=500, scrolling=True)

        csv_source = wo if "Work Order" in report_type else (
            assets if "Asset" in report_type else (
                energy if "Energy" in report_type else data["maintenance_history"]
            )
        )
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("⬇️ Download CSV", data=df_to_csv_bytes(csv_source),
                                file_name=f"{report_type.replace(' ', '_').lower()}.csv", mime="text/csv")
        with d2:
            st.download_button("⬇️ Download Printable HTML", data=html.encode("utf-8"),
                                file_name=f"{report_type.replace(' ', '_').lower()}.html", mime="text/html")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
    st.markdown("<div class='ops-card-title'>Report History</div>", unsafe_allow_html=True)
    hist = report_service.get_report_history()
    if hist.empty:
        st.info("ℹ️ No reports generated yet this session.")
    else:
        st.dataframe(hist, hide_index=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
