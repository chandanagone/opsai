"""Top header bar component."""

import streamlit as st
from datetime import datetime
from utils.constants import FACILITIES
from services import authentication_service as auth


def render_header(page_title: str, show_facility_selector: bool = True):
    col_title, col_search, col_facility, col_notif, col_user = st.columns([2.4, 2, 1.6, 0.7, 1.3])

    with col_title:
        st.markdown(
            f"<div style='font-size:13px;color:#64748b;margin-top:6px;'>"
            f"{datetime.now().strftime('%A, %d %B %Y')}</div>",
            unsafe_allow_html=True,
        )

    with col_search:
        st.text_input("Search", placeholder="🔍 Search work orders, assets, alerts…",
                       label_visibility="collapsed", key=f"header_search_{page_title}")

    with col_facility:
        if show_facility_selector:
            st.selectbox("Facility", ["All Facilities"] + FACILITIES,
                         label_visibility="collapsed", key=f"header_facility_{page_title}")

    with col_notif:
        alert_count = st.session_state.get("_open_alert_count", 0)
        st.markdown(
            f"<div style='text-align:center; padding-top:6px; font-size:20px;'>🔔"
            f"<span style='background:#dc2626;color:white;border-radius:999px;font-size:10px;"
            f"padding:1px 6px;position:relative;top:-10px;left:-6px;'>{alert_count}</span></div>",
            unsafe_allow_html=True,
        )

    with col_user:
        st.markdown(
            f"<div style='text-align:right;padding-top:4px;'>"
            f"<span style='background:#2563eb;color:white;border-radius:50%;padding:6px 11px;"
            f"font-weight:700;font-size:13px;'>{auth.current_user_label()[:1].upper()}</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)
