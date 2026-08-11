"""Sidebar navigation component."""

import streamlit as st
from utils.constants import APP_NAME, NAV_ICONS
from services import authentication_service as auth


NAV_ORDER = [
    "Overview", "Dashboard", "AI Agents", "Modules", "Work Orders", "Assets",
    "Monitoring", "Analytics", "Reports", "Alerts", "Users", "Integrations", "Settings",
]

NAV_GROUPS = [
    ("MAIN", ["Overview", "Dashboard"]),
    ("INTELLIGENCE", ["AI Agents", "Modules"]),
    ("OPERATIONS", ["Work Orders", "Assets", "Monitoring"]),
    ("INSIGHTS", ["Analytics", "Reports", "Alerts"]),
    ("ADMINISTRATION", ["Users", "Integrations", "Settings"]),
]


def render_sidebar():
    with st.sidebar:
        st.markdown(
            f"<div style='padding:6px 4px 14px 4px;'>"
            f"<div style='font-size:19px;font-weight:800;color:#ffffff;'>🏢 {APP_NAME}</div>"
            f"<div style='font-size:11px;color:#94a3b8;letter-spacing:0.5px;'>FACILITY OPERATIONS PLATFORM</div>"
            f"</div>", unsafe_allow_html=True
        )
        st.markdown("<hr style='border-color:#1e3a5f; margin:4px 0 12px 0;'>", unsafe_allow_html=True)

        current = st.session_state.get("current_page", "Overview")

        for group_name, items in NAV_GROUPS:
            st.markdown(
                f"<div style='font-size:10px;color:#64748b;font-weight:700;"
                f"letter-spacing:1px;margin:10px 0 4px 4px;'>{group_name}</div>",
                unsafe_allow_html=True,
            )
            for item in items:
                if not auth.can_access_page(item):
                    continue
                icon = NAV_ICONS.get(item, "•")
                is_active = item == current
                label = f"{icon}  {item}"
                if is_active:
                    st.markdown(
                        f"<div style='background-color:#16324f;border-left:3px solid #2563eb;"
                        f"border-radius:6px;padding:8px 10px;margin-bottom:2px;font-size:14px;"
                        f"font-weight:700;color:#ffffff;'>{label}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button(label, key=f"nav_{item}", use_container_width=True):
                        st.session_state.current_page = item
                        st.rerun()

        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1e3a5f;'>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:13px;font-weight:700;color:#ffffff;'>👤 {auth.current_user_label()}</div>"
            f"<div style='font-size:11px;color:#94a3b8;'>{st.session_state.get('auth_role','')}</div>",
            unsafe_allow_html=True,
        )
        if st.button("🚪 Log Out", use_container_width=True, key="nav_logout"):
            auth.logout()
            st.rerun()
