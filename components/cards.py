"""Reusable card components: KPI cards, agent cards, module cards, info cards."""

import streamlit as st
from utils.helpers import status_badge


def kpi_row(kpi_list):
    """kpi_list: list of dicts {label, value, delta (optional)}"""
    cols = st.columns(len(kpi_list))
    for col, kpi in zip(cols, kpi_list):
        with col:
            st.metric(kpi["label"], kpi["value"], kpi.get("delta"))


def info_card(title: str, subtitle: str, body_html: str = ""):
    st.markdown(
        f"<div class='ops-card'>"
        f"<div class='ops-card-title'>{title}</div>"
        f"<div class='ops-card-subtitle'>{subtitle}</div>"
        f"{body_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def status_pill_row(items: list):
    """items: list of (label, status_value)"""
    html = "<div class='ops-badge-row'>"
    for label, status in items:
        html += f"{label}: {status_badge(status)} &nbsp;&nbsp;"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def quick_action_buttons(actions: list, key_prefix: str = "qa"):
    """actions: list of (label, page_target) tuples. Returns clicked target or None."""
    cols = st.columns(len(actions))
    clicked = None
    for col, (label, target) in zip(cols, actions):
        with col:
            if st.button(label, use_container_width=True, key=f"{key_prefix}_{label}"):
                clicked = target
    return clicked
