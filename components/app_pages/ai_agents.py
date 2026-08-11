"""AI Agents page: four agent cards + details + rule-based AI assistant."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from components.styles import page_header
from components.charts import line_chart

AGENTS = {
    "Energy Optimization Agent": {
        "icon": "⚡",
        "description": "Monitors and optimizes energy and utility consumption across facilities.",
        "confidence": 92,
        "recommendations": 6,
        "metric_key": "Energy_Usage_kWh",
    },
    "Predictive Maintenance Agent": {
        "icon": "🔧",
        "description": "Predicts equipment failures and schedules preventive maintenance.",
        "confidence": 88,
        "recommendations": 4,
        "metric_key": "Health_Score",
    },
    "Occupancy Optimization Agent": {
        "icon": "👥",
        "description": "Analyzes space utilization and optimizes workspace allocation.",
        "confidence": 85,
        "recommendations": 3,
        "metric_key": "Space_Utilization_Pct",
    },
    "Security Monitoring Agent": {
        "icon": "🛡️",
        "description": "Monitors security systems and detects anomalies in real time.",
        "confidence": 96,
        "recommendations": 2,
        "metric_key": "Security_Events",
    },
}


def render(data: dict):
    work_orders = data["work_orders"]
    assets = data["assets"]
    original_metrics = data["original_metrics"]

    page_header("AI Agents", "Autonomous agents monitoring and optimizing your facility operations.")

    if "agent_status" not in st.session_state:
        st.session_state.agent_status = {name: True for name in AGENTS}
    if "agent_last_run" not in st.session_state:
        st.session_state.agent_last_run = {name: (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M") for name in AGENTS}
    if "selected_agent" not in st.session_state:
        st.session_state.selected_agent = None

    cols = st.columns(2)
    for idx, (name, info) in enumerate(AGENTS.items()):
        with cols[idx % 2]:
            st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='ops-card-title'>{info['icon']} {name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='ops-card-subtitle'>{info['description']}</div>", unsafe_allow_html=True)

            status_on = st.session_state.agent_status[name]
            m1, m2, m3 = st.columns(3)
            m1.metric("Status", "Enabled" if status_on else "Disabled")
            m2.metric("Confidence", f"{info['confidence']}%")
            m3.metric("Recommendations", info["recommendations"])
            st.caption(f"Last run: {st.session_state.agent_last_run[name]}")

            b1, b2, b3 = st.columns(3)
            with b1:
                toggle = st.toggle("Enabled", value=status_on, key=f"toggle_{name}")
                st.session_state.agent_status[name] = toggle
            with b2:
                if st.button("Run Now", key=f"run_{name}", use_container_width=True):
                    st.session_state.agent_last_run[name] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.success(f"{name} executed successfully.")
            with b3:
                if st.button("View Details", key=f"details_{name}", use_container_width=True):
                    st.session_state.selected_agent = name
            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.selected_agent:
        _render_agent_details(st.session_state.selected_agent, original_metrics, assets)

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)
    _render_ai_assistant(original_metrics, work_orders, assets)


def _render_agent_details(name, original_metrics, assets):
    info = AGENTS[name]
    st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='ops-card-title'>{info['icon']} {name} — Details</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.4, 1])
    with c1:
        if info["metric_key"] in original_metrics.columns:
            st.plotly_chart(
                line_chart(original_metrics, "Day", info["metric_key"], title="Input Metric History"),
                use_container_width=True,
            )
        elif info["metric_key"] == "Health_Score" and not assets.empty:
            trend = assets[["Asset_Name", "Health_Score"]].sort_values("Health_Score")
            from components.charts import bar_chart
            st.plotly_chart(bar_chart(trend.tail(12), "Asset_Name", "Health_Score", title="Asset Health Scores"), use_container_width=True)
        else:
            st.info("No metric history available for this agent.")
    with c2:
        st.markdown("**AI-Generated Insights**")
        st.write(f"- Confidence score: **{info['confidence']}%**")
        st.write(f"- Recommendations pending: **{info['recommendations']}**")
        st.markdown("**Recommended Actions**")
        st.info("💡 Review flagged items and schedule follow-up actions this week.")
        st.markdown("**Expected Impact**")
        st.success("Estimated 8-15% improvement in the tracked metric if actions are applied.")

    if st.button("Close Details", key="close_agent_details"):
        st.session_state.selected_agent = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_ai_assistant(original_metrics, work_orders, assets):
    st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
    st.markdown("<div class='ops-card-title'>💬 Interactive AI Assistant</div>", unsafe_allow_html=True)
    st.caption("Ask operational questions about your facility data — no external AI API required.")

    query = st.text_input(
        "Ask a question",
        placeholder="e.g. Which day had the highest energy use? How many work orders are open?",
        key="ai_assistant_query",
        label_visibility="collapsed",
    )

    if query:
        answer = _answer_query(query.lower(), original_metrics, work_orders, assets)
        st.success(f"🤖 **FacilityOps AI:** {answer}")
    st.markdown("</div>", unsafe_allow_html=True)


def _answer_query(q, original_metrics, work_orders, assets):
    if ("highest" in q and "energy" in q) or "kwh" in q:
        if "Energy_Usage_kWh" in original_metrics.columns and not original_metrics.empty:
            idx = original_metrics["Energy_Usage_kWh"].idxmax()
            return (f"The highest energy usage was on Day {original_metrics.loc[idx,'Day']} "
                    f"at {original_metrics.loc[idx,'Energy_Usage_kWh']} kWh.")
        return "No energy data is currently available."

    if "open" in q and "work order" in q:
        if not work_orders.empty:
            n = int(work_orders["Status"].isin(["Open", "Assigned", "In Progress"]).sum())
            return f"There are currently **{n}** open work orders (Open, Assigned, or In Progress)."
        return "No work order data is currently available."

    if "critical" in q and "asset" in q:
        if not assets.empty:
            crit = assets[assets["Operating_Status"] == "Critical"]
            if crit.empty:
                return "No assets are currently in critical condition."
            names = ", ".join(crit["Asset_Name"].head(5).tolist())
            return f"{len(crit)} asset(s) are in critical condition: {names}."
        return "No asset data is currently available."

    if "average" in q and "occupancy" in q:
        if "Space_Utilization_Pct" in original_metrics.columns:
            avg = round(original_metrics["Space_Utilization_Pct"].mean(), 1)
            return f"The average space utilization (occupancy) is **{avg}%**."
        return "No occupancy data is currently available."

    if "security" in q and ("alert" in q or "event" in q):
        if "Security_Events" in original_metrics.columns:
            total = int(original_metrics["Security_Events"].sum())
            return f"A total of **{total}** security events have been logged."
        return "No security event data is currently available."

    if "operating cost" in q or ("facility" in q and "cost" in q):
        if not work_orders.empty:
            by_fac = work_orders.groupby("Facility")["Actual_Cost"].sum().sort_values(ascending=False)
            if not by_fac.empty:
                top_fac = by_fac.index[0]
                return f"**{top_fac}** has the highest recorded operating cost at ₹{by_fac.iloc[0]:,.0f}."
        return "No cost data is currently available."

    return ("I can answer questions about energy usage, work orders, asset condition, occupancy, "
            "security events, or facility operating costs. Try asking about one of these topics.")
