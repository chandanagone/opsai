"""Central shared CSS for the enhanced FacilityOps AI application."""

import streamlit as st
from utils.constants import (
    COLOR_SIDEBAR, COLOR_SIDEBAR_ACTIVE, COLOR_BG, COLOR_CARD, COLOR_PRIMARY,
    COLOR_TEXT, COLOR_MUTED, COLOR_BORDER,
)


def inject_global_styles():
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {COLOR_BG}; }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {COLOR_SIDEBAR} !important;
        }}
        [data-testid="stSidebar"] * {{
            color: #e2e8f0 !important;
        }}
        [data-testid="stSidebar"] label {{
            color: #94a3b8 !important;
        }}
        [data-testid="stSidebar"] .stButton button {{
            background-color: transparent;
            border: none;
            text-align: left;
            width: 100%;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
        }}
        [data-testid="stSidebar"] .stButton button:hover {{
            background-color: {COLOR_SIDEBAR_ACTIVE};
            color: #ffffff !important;
        }}

        /* Metric cards */
        div[data-testid="stMetric"] {{
            background-color: {COLOR_CARD};
            padding: 18px 20px;
            border-radius: 12px;
            border: 1px solid {COLOR_BORDER};
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        div[data-testid="stMetric"] label {{
            color: {COLOR_MUTED} !important;
            font-weight: 600;
        }}

        /* Generic card container */
        .ops-card {{
            background-color: {COLOR_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .ops-card-title {{
            font-size: 16px;
            font-weight: 700;
            color: {COLOR_TEXT};
            margin-bottom: 4px;
        }}
        .ops-card-subtitle {{
            font-size: 13px;
            color: {COLOR_MUTED};
            margin-bottom: 10px;
        }}

        /* Page header */
        .ops-page-title {{
            font-size: 26px;
            font-weight: 800;
            color: {COLOR_SIDEBAR};
            margin-bottom: 2px;
        }}
        .ops-page-subtitle {{
            font-size: 14px;
            color: {COLOR_MUTED};
            margin-bottom: 20px;
        }}

        /* Buttons */
        .stButton>button[kind="primary"], .stFormSubmitButton>button {{
            background-color: {COLOR_PRIMARY};
            border-color: {COLOR_PRIMARY};
        }}

        hr {{ margin: 14px 0; border-color: {COLOR_BORDER}; }}

        .ops-divider {{
            border-top: 1px solid {COLOR_BORDER};
            margin: 18px 0;
        }}

        section[data-testid="stSidebarNav"] {{ display: none; }}

        .ops-badge-row span {{ margin-right: 6px; }}

        /* Reduce default top padding */
        .block-container {{ padding-top: 1.6rem; }}
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"<div class='ops-page-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='ops-page-subtitle'>{subtitle}</div>", unsafe_allow_html=True)
