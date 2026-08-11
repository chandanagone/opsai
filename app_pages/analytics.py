"""Analytics page: trend analysis, comparisons, and lightweight forecasting."""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta

from components.styles import page_header
from components.charts import line_chart, bar_chart
from utils.constants import FACILITIES
from utils.export_utils import df_to_csv_bytes


def _forecast(series: pd.Series, periods: int) -> pd.Series:
    """Simple linear-regression based forecast for a numeric series."""
    y = series.values.astype(float)
    x = np.arange(len(y))
    if len(y) < 2:
        return pd.Series([y[-1]] * periods if len(y) else [0] * periods)
    coeffs = np.polyfit(x, y, 1)
    future_x = np.arange(len(y), len(y) + periods)
    forecast_vals = np.polyval(coeffs, future_x)
    return pd.Series(np.maximum(forecast_vals, 0))


def render(data: dict):
    work_orders = data["work_orders"]
    assets = data["assets"]
    alerts = data["alerts"]
    energy = data["energy_history"]
    maintenance = data["maintenance_history"]
    original_metrics = data["original_metrics"]

    page_header("Analytics", "Deep-dive analysis, trends, and short-term forecasts.")

    f1, f2, f3 = st.columns([1.3, 1.6, 1.3])
    with f1:
        facility = st.selectbox("Facility", ["All Facilities"] + FACILITIES, key="an_facility")
    with f2:
        min_d = pd.to_datetime(energy["Date"]).min() if not energy.empty else pd.Timestamp.now() - timedelta(days=30)
        max_d = pd.to_datetime(energy["Date"]).max() if not energy.empty else pd.Timestamp.now()
        date_range = st.date_input("Date range", value=(min_d.date(), max_d.date()), key="an_dates")
    with f3:
        metric = st.selectbox("Forecast metric", ["Energy Usage (kWh)", "Work Order Volume"], key="an_metric")

    energy_f = energy.copy()
    if facility != "All Facilities" and not energy_f.empty:
        energy_f = energy_f[energy_f["Facility"] == facility]
    if isinstance(date_range, tuple) and len(date_range) == 2 and not energy_f.empty:
        start, end = date_range
        edates = pd.to_datetime(energy_f["Date"])
        energy_f = energy_f[(edates >= pd.Timestamp(start)) & (edates <= pd.Timestamp(end))]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Energy Trend Analysis</div>", unsafe_allow_html=True)
        if not energy_f.empty:
            daily = energy_f.groupby("Date", as_index=False)["Energy_Usage_kWh"].sum().sort_values("Date")
            st.plotly_chart(line_chart(daily, "Date", "Energy_Usage_kWh"), use_container_width=True)
        else:
            st.plotly_chart(line_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Energy Usage by Facility</div>", unsafe_allow_html=True)
        if not energy.empty:
            by_fac = energy.groupby("Facility", as_index=False)["Energy_Usage_kWh"].sum()
            st.plotly_chart(bar_chart(by_fac, "Facility", "Energy_Usage_kWh"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Maintenance Cost Trend</div>", unsafe_allow_html=True)
        if not maintenance.empty:
            m = maintenance.copy()
            m["Date"] = pd.to_datetime(m["Date"])
            monthly = m.groupby(m["Date"].dt.to_period("M").astype(str))["Cost_INR"].sum().reset_index()
            monthly.columns = ["Month", "Cost_INR"]
            st.plotly_chart(bar_chart(monthly, "Month", "Cost_INR"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Work Order Completion Trend</div>", unsafe_allow_html=True)
        if not work_orders.empty:
            wo = work_orders.copy()
            wo["Created_Date"] = pd.to_datetime(wo["Created_Date"])
            completed = wo[wo["Status"] == "Completed"]
            trend = completed.groupby(completed["Created_Date"].dt.to_period("W").astype(str)).size().reset_index()
            trend.columns = ["Week", "Completed"]
            st.plotly_chart(bar_chart(trend, "Week", "Completed"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c5, c6 = st.columns(2)
    with c5:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Asset Failure / Critical Trend</div>", unsafe_allow_html=True)
        if not assets.empty:
            fail = assets["Operating_Status"].value_counts().reset_index()
            fail.columns = ["Status", "Count"]
            st.plotly_chart(bar_chart(fail, "Status", "Count"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c6:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Security Incident Analysis</div>", unsafe_allow_html=True)
        sec_alerts = alerts[alerts["Category"] == "Security"] if not alerts.empty else alerts
        if not sec_alerts.empty:
            sev = sec_alerts["Severity"].value_counts().reset_index()
            sev.columns = ["Severity", "Count"]
            st.plotly_chart(bar_chart(sev, "Severity", "Count"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='ops-card-title'>Forecast — {metric} (next 7 days)</div>", unsafe_allow_html=True)
    if metric == "Energy Usage (kWh)" and not energy.empty:
        daily_all = energy.groupby("Date", as_index=False)["Energy_Usage_kWh"].sum().sort_values("Date")
        daily_all["Date"] = pd.to_datetime(daily_all["Date"])
        forecast_vals = _forecast(daily_all["Energy_Usage_kWh"], 7)
        future_dates = pd.date_range(daily_all["Date"].max() + timedelta(days=1), periods=7)
        combined = pd.concat([
            pd.DataFrame({"Date": daily_all["Date"], "Energy_Usage_kWh": daily_all["Energy_Usage_kWh"], "Type": "Actual"}),
            pd.DataFrame({"Date": future_dates, "Energy_Usage_kWh": forecast_vals.values, "Type": "Forecast"}),
        ])
        st.plotly_chart(line_chart(combined, "Date", "Energy_Usage_kWh", color="Type"), use_container_width=True)
        st.caption("Forecast generated using a simple linear-regression trend on historical daily totals. Values labeled 'Forecast' are projections, not actual readings.")
    elif metric == "Work Order Volume" and not work_orders.empty:
        wo = work_orders.copy()
        wo["Created_Date"] = pd.to_datetime(wo["Created_Date"])
        daily_counts = wo.groupby(wo["Created_Date"].dt.date).size().reset_index()
        daily_counts.columns = ["Date", "Count"]
        forecast_vals = _forecast(daily_counts["Count"], 7)
        future_dates = pd.date_range(pd.to_datetime(daily_counts["Date"].max()) + timedelta(days=1), periods=7)
        combined = pd.concat([
            pd.DataFrame({"Date": pd.to_datetime(daily_counts["Date"]), "Count": daily_counts["Count"], "Type": "Actual"}),
            pd.DataFrame({"Date": future_dates, "Count": forecast_vals.values, "Type": "Forecast"}),
        ])
        st.plotly_chart(line_chart(combined, "Date", "Count", color="Type"), use_container_width=True)
        st.caption("Forecast generated using a simple linear-regression trend. Values labeled 'Forecast' are projections, not actual readings.")
    else:
        st.info("ℹ️ Not enough data to generate a forecast yet.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
    st.markdown("<div class='ops-card-title'>Top Operational Insights</div>", unsafe_allow_html=True)
    insights = []
    if not energy.empty:
        top_fac = energy.groupby("Facility")["Energy_Usage_kWh"].sum().idxmax()
        insights.append(f"**{top_fac}** consumes the most energy across the selected period.")
    if not work_orders.empty:
        top_cat = work_orders["Category"].value_counts().idxmax()
        insights.append(f"**{top_cat}** is the most common work order category.")
    if not assets.empty:
        crit_count = int((assets["Operating_Status"] == "Critical").sum())
        if crit_count:
            insights.append(f"**{crit_count}** asset(s) currently require critical attention.")
    if not insights:
        insights.append("No significant patterns detected in the current data.")
    for i in insights:
        st.write(f"• {i}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.download_button("⬇️ Download Energy Analytics Data", data=df_to_csv_bytes(energy),
                        file_name="analytics_energy_data.csv", mime="text/csv")
