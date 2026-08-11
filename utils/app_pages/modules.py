"""Modules page: platform module management cards."""

import streamlit as st
from components.styles import page_header

MODULES = [
    {"name": "Energy Management", "icon": "⚡", "desc": "Track and optimize facility energy consumption.", "version": "v2.4.0", "updated": "2026-06-12"},
    {"name": "Maintenance Management", "icon": "🔧", "desc": "Plan, assign, and track maintenance work.", "version": "v3.1.2", "updated": "2026-07-01"},
    {"name": "Space and Occupancy", "icon": "🏢", "desc": "Monitor space utilization and occupancy trends.", "version": "v1.8.0", "updated": "2026-05-20"},
    {"name": "Security Operations", "icon": "🛡️", "desc": "Monitor security events and manage incidents.", "version": "v2.0.1", "updated": "2026-06-28"},
    {"name": "Asset Management", "icon": "📦", "desc": "Register, track and maintain facility assets.", "version": "v2.9.0", "updated": "2026-07-15"},
    {"name": "Work-Order Management", "icon": "🛠️", "desc": "Create, assign and resolve work orders.", "version": "v3.3.0", "updated": "2026-07-20"},
    {"name": "Analytics and Reporting", "icon": "📈", "desc": "Analyze trends and generate operational reports.", "version": "v1.6.4", "updated": "2026-07-10"},
    {"name": "User Administration", "icon": "👥", "desc": "Manage user accounts, roles and permissions.", "version": "v1.4.0", "updated": "2026-06-05"},
]

PAGE_TARGET = {
    "Energy Management": "Analytics", "Maintenance Management": "Work Orders",
    "Space and Occupancy": "Dashboard", "Security Operations": "Alerts",
    "Asset Management": "Assets", "Work-Order Management": "Work Orders",
    "Analytics and Reporting": "Analytics", "User Administration": "Users",
}


def render(data: dict):
    page_header("Modules", "Enable, disable, and open the platform modules available to your organization.")

    if "module_status" not in st.session_state:
        st.session_state.module_status = {m["name"]: True for m in MODULES}

    cols = st.columns(2)
    for idx, m in enumerate(MODULES):
        with cols[idx % 2]:
            st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='ops-card-title'>{m['icon']} {m['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='ops-card-subtitle'>{m['desc']}</div>", unsafe_allow_html=True)
            st.caption(f"Version {m['version']} · Last updated {m['updated']}")

            enabled = st.session_state.module_status[m["name"]]
            b1, b2 = st.columns(2)
            with b1:
                new_state = st.toggle("Enabled", value=enabled, key=f"mod_toggle_{m['name']}")
                st.session_state.module_status[m["name"]] = new_state
            with b2:
                if st.button("Open Module", key=f"mod_open_{m['name']}", use_container_width=True,
                             disabled=not new_state):
                    st.session_state.current_page = PAGE_TARGET.get(m["name"], "Overview")
                    st.rerun()
            status_text = "🟢 Enabled" if new_state else "🔴 Disabled"
            st.caption(status_text)
            st.markdown("</div>", unsafe_allow_html=True)
