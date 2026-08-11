"""Monitoring page: real-time-style facility monitoring with simulated sensors."""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from components.styles import page_header
from components.charts import line_chart
from utils.constants import FACILITIES

THRESHOLDS = {
    "Temperature (°C)": {"warn": 26, "crit": 30},
    "Humidity (%)": {"warn": 65, "crit": 75},
    "Air Quality (AQI)": {"warn": 100, "crit": 150},
    "Vibration (mm/s)": {"warn": 4.5, "crit": 7.0},
}


def _simulate_snapshot(seed_offset=0):
    rng = np.random.default_rng(seed_offset + int(datetime.now().strftime("%H")))
    return {
        "Energy Consumption (kW)": round(float(rng.uniform(150, 420)), 1),
        "Temperature (°C)": round(float(rng.uniform(20, 32)), 1),
        "Humidity (%)": round(float(rng.uniform(35, 78)), 1),
        "Occupancy (people)": int(rng.uniform(30, 260)),
        "Air Quality (AQI)": round(float(rng.uniform(20, 160)), 0),
        "Equipment Vibration (mm/s)": round(float(rng.uniform(0.5, 8)), 2),
        "Equipment Health (%)": round(float(rng.uniform(55, 99)), 1),
        "Security Events (24h)": int(rng.uniform(0, 6)),
    }


def render(data: dict):
    page_header("Monitoring", "Live-style operational monitoring across sensors and equipment.")

    c1, c2, c3, c4 = st.columns([1.4, 1, 1, 1])
    with c1:
        facility = st.selectbox("Facility", FACILITIES, key="mon_facility")
    with c2:
        auto_refresh = st.toggle("Auto-refresh", value=False, key="mon_auto_refresh")
    with c3:
        refresh_clicked = st.button("🔄 Refresh Now", use_container_width=True, key="mon_refresh_btn")
    with c4:
        if "mon_last_updated" not in st.session_state:
            st.session_state.mon_last_updated = datetime.now().strftime("%H:%M:%S")
        st.caption(f"Last updated: {st.session_state.mon_last_updated}")

    if "mon_snapshot" not in st.session_state:
        st.session_state.mon_snapshot = _simulate_snapshot(hash(facility) % 1000)

    if refresh_clicked or auto_refresh:
        st.session_state.mon_snapshot = _simulate_snapshot(hash(facility) % 1000 + np.random.randint(0, 999))
        st.session_state.mon_last_updated = datetime.now().strftime("%H:%M:%S")

    snap = st.session_state.mon_snapshot

    metrics = list(snap.items())
    cols = st.columns(4)
    for i, (label, value) in enumerate(metrics):
        with cols[i % 4]:
            st.metric(label, value)

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)

    c5, c6 = st.columns(2)
    hist_days = pd.date_range(end=datetime.now(), periods=24, freq="H")
    with c5:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Energy Consumption (24h)</div>", unsafe_allow_html=True)
        rng = np.random.default_rng(hash(facility) % 500)
        energy_series = pd.DataFrame({
            "Time": hist_days,
            "kW": rng.uniform(150, 420, size=len(hist_days)),
        })
        st.plotly_chart(line_chart(energy_series, "Time", "kW"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c6:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Temperature & Humidity (24h)</div>", unsafe_allow_html=True)
        rng2 = np.random.default_rng(hash(facility) % 700)
        th_series = pd.DataFrame({
            "Time": hist_days,
            "Temperature": rng2.uniform(20, 30, size=len(hist_days)),
        })
        st.plotly_chart(line_chart(th_series, "Time", "Temperature"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
    st.markdown("<div class='ops-card-title'>Sensor Status & Active Anomalies</div>", unsafe_allow_html=True)
    anomalies = []
    # Build sensor table using the direct snapshot keys that match THRESHOLDS naming
    threshold_keys = {
        "Temperature (°C)": snap.get("Temperature (°C)"),
        "Humidity (%)": snap.get("Humidity (%)"),
        "Air Quality (AQI)": snap.get("Air Quality (AQI)"),
        "Vibration (mm/s)": snap.get("Equipment Vibration (mm/s)"),
    }
    sensor_table = []
    for label, limits in THRESHOLDS.items():
        val = threshold_keys[label]
        if val is None:
            continue
        if val >= limits["crit"]:
            state = "Critical"
        elif val >= limits["warn"]:
            state = "Warning"
        else:
            state = "Normal"
        sensor_table.append({"Sensor": label, "Reading": val, "Warning Threshold": limits["warn"],
                              "Critical Threshold": limits["crit"], "State": state})
        if state != "Normal":
            anomalies.append(f"{label} reading of {val} is at **{state}** level (threshold {limits['warn' if state=='Warning' else 'crit']}).")

    st.dataframe(pd.DataFrame(sensor_table), hide_index=True, use_container_width=True)

    if anomalies:
        st.markdown("**Active Anomalies**")
        for a in anomalies:
            st.warning(f"⚠️ {a}")
    else:
        st.success("✅ No active anomalies detected.")
    st.markdown("</div>", unsafe_allow_html=True)

    if auto_refresh:
        st.caption("Auto-refresh is enabled — data updates each time this page reruns.")
