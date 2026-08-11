"""Overview page: executive summary of facility operations."""

import streamlit as st
import pandas as pd

from components.styles import page_header
from components.cards import kpi_row, info_card, quick_action_buttons
from components.charts import line_chart, bar_chart
from components.notifications import alert_summary_strip, recent_alerts_timeline
from utils.helpers import safe_mean, safe_sum, format_currency
from utils.constants import FACILITIES


def render(data: dict):
    work_orders = data["work_orders"]
    assets = data["assets"]
    alerts = data["alerts"]
    energy = data["energy_history"]
    original_metrics = data["original_metrics"]

    page_header("Overview", "A quick summary of key metrics and recent activity across your facilities.")

    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.caption("Facility & date range")
    with top_r:
        facility_choice = st.selectbox(
            "Facility", ["All Facilities"] + FACILITIES, label_visibility="collapsed", key="overview_facility"
        )

    if facility_choice != "All Facilities" and not energy.empty:
        energy_f = energy[energy["Facility"] == facility_choice]
    else:
        energy_f = energy

    if facility_choice != "All Facilities" and not work_orders.empty:
        wo_f = work_orders[work_orders["Facility"] == facility_choice]
    else:
        wo_f = work_orders

    if facility_choice != "All Facilities" and not assets.empty:
        assets_f = assets[assets["Facility"] == facility_choice]
    else:
        assets_f = assets

    if facility_choice != "All Facilities" and not alerts.empty:
        alerts_f = alerts[alerts["Facility"] == facility_choice]
    else:
        alerts_f = alerts

    # ---- KPI cards ----
    open_wo = int(wo_f["Status"].isin(["Open", "Assigned", "In Progress"]).sum()) if not wo_f.empty else 0
    active_assets = int((assets_f["Operating_Status"] == "Operational").sum()) if not assets_f.empty else 0
    critical_alerts = int((alerts_f["Severity"] == "Critical").sum()) if not alerts_f.empty else 0
    energy_today = round(energy_f.sort_values("Date")["Energy_Usage_kWh"].iloc[-1], 1) if not energy_f.empty else 0
    occupancy_avg = safe_mean(original_metrics["Space_Utilization_Pct"]) if "Space_Utilization_Pct" in original_metrics.columns else 0
    est_savings = format_currency(safe_sum(wo_f["Estimated_Cost"]) * 0.12) if not wo_f.empty else format_currency(0)

    kpi_row([
        {"label": "Total Facilities", "value": len(FACILITIES)},
        {"label": "Active Assets", "value": active_assets},
        {"label": "Open Work Orders", "value": open_wo},
        {"label": "Critical Alerts", "value": critical_alerts},
        {"label": "Energy Today (kWh)", "value": f"{energy_today:,.0f}"},
        {"label": "Est. Monthly Savings", "value": est_savings},
    ])

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)

    # ---- Trend chart + occupancy ----
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Energy Usage Trend</div>", unsafe_allow_html=True)
        if not energy_f.empty:
            trend = energy_f.groupby("Date", as_index=False)["Energy_Usage_kWh"].sum().sort_values("Date")
            st.plotly_chart(line_chart(trend, "Date", "Energy_Usage_kWh"), use_container_width=True)
        else:
            st.plotly_chart(line_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Work Order Status</div>", unsafe_allow_html=True)
        if not wo_f.empty:
            status_counts = wo_f["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.plotly_chart(bar_chart(status_counts, "Status", "Count"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Recent work orders + alerts ----
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Recent Work Orders</div>", unsafe_allow_html=True)
        if not wo_f.empty:
            recent_wo = wo_f.sort_values("Created_Date", ascending=False).head(5)[
                ["Work_Order_ID", "Title", "Priority", "Status", "Assigned_Technician"]
            ]
            st.dataframe(recent_wo, hide_index=True, use_container_width=True)
        else:
            st.info("ℹ️ No work orders recorded yet.")
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Critical Alerts</div>", unsafe_allow_html=True)
        alert_summary_strip(alerts_f)
        recent_alerts_timeline(alerts_f, n=5)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- AI recommendations + performance summary ----
    c5, c6 = st.columns([1.3, 1])
    with c5:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>AI Recommendations</div>", unsafe_allow_html=True)
        recs = _build_recommendations(assets_f, wo_f, energy_f)
        for r in recs:
            st.info(f"💡 {r}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c6:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Facility Performance Summary</div>", unsafe_allow_html=True)
        for fac in FACILITIES:
            fac_assets = assets[assets["Facility"] == fac] if not assets.empty else pd.DataFrame()
            health = safe_mean(fac_assets["Health_Score"]) if not fac_assets.empty else 0
            st.write(f"**{fac}**")
            st.progress(min(100, max(0, int(health))) / 100, text=f"Avg asset health: {health:.0f}%")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Quick actions ----
    st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
    st.markdown("<div class='ops-card-title'>Quick Actions</div>", unsafe_allow_html=True)
    target = quick_action_buttons([
        ("➕ Create Work Order", "Work Orders"),
        ("📦 Register Asset", "Assets"),
        ("🚨 View Alerts", "Alerts"),
        ("📄 Generate Report", "Reports"),
    ], key_prefix="overview_qa")
    st.markdown("</div>", unsafe_allow_html=True)
    if target:
        st.session_state.current_page = target
        st.rerun()


def _build_recommendations(assets_f, wo_f, energy_f):
    recs = []
    if not assets_f.empty:
        low_health = assets_f[assets_f["Health_Score"] < 45]
        if not low_health.empty:
            recs.append(
                f"{len(low_health)} asset(s) show degraded health scores below 45% — "
                f"schedule preventive maintenance to avoid unplanned downtime."
            )
    if not wo_f.empty:
        critical_open = wo_f[(wo_f["Priority"] == "Critical") & (wo_f["Status"] != "Completed")]
        if not critical_open.empty:
            recs.append(
                f"{len(critical_open)} critical-priority work order(s) remain open — "
                f"consider reassigning technicians to accelerate resolution."
            )
    if not energy_f.empty:
        recent = energy_f.sort_values("Date").tail(7)
        if len(recent) >= 2 and recent["Energy_Usage_kWh"].iloc[-1] > recent["Energy_Usage_kWh"].mean() * 1.15:
            recs.append("Energy usage over the last day is trending above the weekly average — review HVAC scheduling.")
    if not recs:
        recs.append("All monitored systems are operating within expected parameters.")
    return recs
