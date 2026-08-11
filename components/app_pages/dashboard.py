"""Dashboard page: detailed operational dashboard with filters."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from components.styles import page_header
from components.cards import kpi_row
from components.charts import line_chart, bar_chart, area_chart
from utils.helpers import safe_mean, safe_sum
from utils.constants import FACILITIES, WORK_ORDER_STATUSES


def render(data: dict):
    work_orders = data["work_orders"]
    assets = data["assets"]
    alerts = data["alerts"]
    energy = data["energy_history"]
    maintenance = data["maintenance_history"]
    original_metrics = data["original_metrics"]

    page_header("Dashboard", "Detailed operational metrics across energy, maintenance, assets and occupancy.")

    # ---- Filters ----
    f1, f2, f3, f4, f5 = st.columns([1.3, 1.6, 1.2, 1, 0.8])
    with f1:
        facility_choice = st.selectbox("Facility", ["All Facilities"] + FACILITIES, key="dash_facility")
    with f2:
        min_date = pd.to_datetime(energy["Date"]).min() if not energy.empty else datetime.now() - timedelta(days=30)
        max_date = pd.to_datetime(energy["Date"]).max() if not energy.empty else datetime.now()
        date_range = st.date_input("Date range", value=(min_date.date(), max_date.date()), key="dash_dates")
    with f3:
        dept_choice = st.selectbox("Department", ["All Departments"] + ["Facilities", "IT", "Security", "Operations", "HR", "Finance"], key="dash_dept")
    with f4:
        status_choice = st.selectbox("WO Status", ["All Statuses"] + WORK_ORDER_STATUSES, key="dash_status")
    with f5:
        st.write("")
        if st.button("🔄 Refresh", use_container_width=True, key="dash_refresh"):
            st.rerun()

    # ---- Apply filters ----
    energy_f = energy.copy()
    wo_f = work_orders.copy()
    assets_f = assets.copy()

    if facility_choice != "All Facilities":
        if not energy_f.empty:
            energy_f = energy_f[energy_f["Facility"] == facility_choice]
        if not wo_f.empty:
            wo_f = wo_f[wo_f["Facility"] == facility_choice]
        if not assets_f.empty:
            assets_f = assets_f[assets_f["Facility"] == facility_choice]

    if isinstance(date_range, tuple) and len(date_range) == 2 and not energy_f.empty:
        start, end = date_range
        edates = pd.to_datetime(energy_f["Date"])
        energy_f = energy_f[(edates >= pd.Timestamp(start)) & (edates <= pd.Timestamp(end))]

    if status_choice != "All Statuses" and not wo_f.empty:
        wo_f = wo_f[wo_f["Status"] == status_choice]

    # ---- KPI cards ----
    kpi_row([
        {"label": "Open Work Orders", "value": int(wo_f["Status"].isin(["Open", "Assigned", "In Progress"]).sum()) if not wo_f.empty else 0},
        {"label": "Avg Asset Health", "value": f"{safe_mean(assets_f['Health_Score']):.0f}%" if not assets_f.empty else "0%"},
        {"label": "Total Energy (kWh)", "value": f"{safe_sum(energy_f['Energy_Usage_kWh']):,.0f}" if not energy_f.empty else "0"},
        {"label": "Avg Occupancy", "value": f"{safe_mean(original_metrics.get('Space_Utilization_Pct', pd.Series())):.0f}%"},
        {"label": "Maintenance Cost", "value": f"₹{safe_sum(maintenance['Cost_INR']):,.0f}" if not maintenance.empty else "₹0"},
    ])

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)

    # ---- Row: energy bar + energy trend ----
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Weekly Energy Trend</div>", unsafe_allow_html=True)
        if not energy_f.empty:
            weekly = energy_f.copy()
            weekly["Date"] = pd.to_datetime(weekly["Date"])
            weekly = weekly.groupby("Date", as_index=False)["Energy_Usage_kWh"].sum().sort_values("Date")
            st.plotly_chart(line_chart(weekly, "Date", "Energy_Usage_kWh"), use_container_width=True)
        else:
            st.plotly_chart(line_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Energy Usage by Facility</div>", unsafe_allow_html=True)
        if not energy_f.empty:
            by_fac = energy_f.groupby("Facility", as_index=False)["Energy_Usage_kWh"].sum()
            st.plotly_chart(bar_chart(by_fac, "Facility", "Energy_Usage_kWh"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Row: maintenance + work order priority ----
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Monthly Maintenance Trend</div>", unsafe_allow_html=True)
        if not maintenance.empty:
            m = maintenance.copy()
            m["Date"] = pd.to_datetime(m["Date"])
            m["Month"] = m["Date"].dt.to_period("M").astype(str)
            monthly = m.groupby("Month", as_index=False)["Cost_INR"].sum()
            st.plotly_chart(bar_chart(monthly, "Month", "Cost_INR"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Work Order Priority Distribution</div>", unsafe_allow_html=True)
        if not wo_f.empty:
            pr = wo_f["Priority"].value_counts().reset_index()
            pr.columns = ["Priority", "Count"]
            st.plotly_chart(bar_chart(pr, "Priority", "Count"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Row: occupancy + cost savings ----
    c5, c6 = st.columns(2)
    with c5:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Occupancy Trend</div>", unsafe_allow_html=True)
        if "Day" in original_metrics.columns and "Space_Utilization_Pct" in original_metrics.columns:
            st.plotly_chart(area_chart(original_metrics, "Day", "Space_Utilization_Pct"), use_container_width=True)
        else:
            st.plotly_chart(area_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c6:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Cost Savings (Est. vs Actual)</div>", unsafe_allow_html=True)
        if not wo_f.empty:
            cost_df = wo_f.groupby("Facility", as_index=False)[["Estimated_Cost", "Actual_Cost"]].sum()
            cost_df = cost_df.melt(id_vars="Facility", var_name="Type", value_name="Amount")
            st.plotly_chart(bar_chart(cost_df, "Facility", "Amount", color="Type"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Recent activity + top / underperforming ----
    c7, c8 = st.columns(2)
    with c7:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Recent Activity Timeline</div>", unsafe_allow_html=True)
        if not wo_f.empty:
            timeline = wo_f.sort_values("Created_Date", ascending=False).head(6)
            for _, row in timeline.iterrows():
                st.markdown(
                    f"🛠️ **{row['Title']}** — {row['Facility']} "
                    f"<span style='color:#94a3b8;font-size:12px;'>({row['Created_Date']})</span>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("ℹ️ No recent activity.")
        st.markdown("</div>", unsafe_allow_html=True)
    with c8:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Top / Underperforming Assets</div>", unsafe_allow_html=True)
        if not assets_f.empty:
            top = assets_f.nlargest(3, "Health_Score")[["Asset_Name", "Health_Score"]]
            low = assets_f.nsmallest(3, "Health_Score")[["Asset_Name", "Health_Score"]]
            st.write("**Top performing**")
            st.dataframe(top, hide_index=True, use_container_width=True)
            st.write("**Needs attention**")
            st.dataframe(low, hide_index=True, use_container_width=True)
        else:
            st.info("ℹ️ No asset data available.")
        st.markdown("</div>", unsafe_allow_html=True)
