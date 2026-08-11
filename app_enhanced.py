"""
app_enhanced.py
----------------
Entry point for the enhanced FacilityOps AI platform.

This file NEVER imports from or modifies app.py. It is a fully separate
application that reuses facility_data.csv (read-only) as a data source
alongside a richer set of sample datasets stored under ./data.

Run with:
    streamlit run app_enhanced.py
"""

import streamlit as st

from components.styles import inject_global_styles
from components.sidebar import render_sidebar
from components.header import render_header
from services import authentication_service as auth
from services import data_service
from app_pages import login as login_page
from app_pages import (
    overview, dashboard, ai_agents, modules, work_orders, assets,
    monitoring, analytics, reports, alerts, users, integrations, settings,
)

st.set_page_config(
    page_title="FacilityOps AI — Enhanced",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGE_MODULES = {
    "Overview": overview,
    "Dashboard": dashboard,
    "AI Agents": ai_agents,
    "Modules": modules,
    "Work Orders": work_orders,
    "Assets": assets,
    "Monitoring": monitoring,
    "Analytics": analytics,
    "Reports": reports,
    "Alerts": alerts,
    "Users": users,
    "Integrations": integrations,
    "Settings": settings,
}


def load_all_data() -> dict:
    """Load every dataset used across the application, safely."""
    return {
        "original_metrics": data_service.load_original_facility_data(),
        "work_orders": data_service.load_work_orders(),
        "assets": data_service.load_assets(),
        "alerts": data_service.load_alerts(),
        "users": data_service.load_users(),
        "energy_history": data_service.load_energy_history(),
        "maintenance_history": data_service.load_maintenance_history(),
        "integrations": data_service.load_integrations(),
    }


def main():
    auth.init_session_state()
    inject_global_styles()
    data_service.ensure_data_ready()

    if not auth.is_logged_in():
        login_page.render_login()
        return

    data = load_all_data()

    # Keep a lightweight open-alert count available for the header badge.
    alerts_df = data["alerts"]
    if not alerts_df.empty:
        open_statuses = ["New", "Acknowledged", "Assigned", "Reopened"]
        st.session_state["_open_alert_count"] = int(alerts_df["Status"].isin(open_statuses).sum())
    else:
        st.session_state["_open_alert_count"] = 0

    render_sidebar()

    current_page = st.session_state.get("current_page", "Overview")
    if current_page not in PAGE_MODULES or not auth.can_access_page(current_page):
        current_page = "Overview"
        st.session_state.current_page = current_page

    render_header(current_page)

    page_module = PAGE_MODULES.get(current_page, overview)
    try:
        page_module.render(data)
    except Exception as exc:
        st.error(f"⚠️ Something went wrong while loading the '{current_page}' page: {exc}")
        st.caption("Try refreshing the page or selecting a different module from the sidebar.")


if __name__ == "__main__":
    main()
