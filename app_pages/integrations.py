"""Integrations page: manage third-party / system integrations (simulated)."""

import streamlit as st
from datetime import datetime

from components.styles import page_header
from services import data_service


def render(data: dict):
    page_header("Integrations", "Connect and configure system and third-party integrations.")

    df = data_service.load_integrations()
    if "integration_status" not in st.session_state:
        st.session_state.integration_status = {
            row["Integration_Name"]: {"status": row["Status"], "last_sync": row["Last_Sync"]}
            for _, row in df.iterrows()
        } if not df.empty else {}

    cols = st.columns(2)
    for idx, (name, state) in enumerate(st.session_state.integration_status.items()):
        desc_row = df[df["Integration_Name"] == name]
        desc = desc_row["Description"].iloc[0] if not desc_row.empty else ""
        with cols[idx % 2]:
            st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='ops-card-title'>🔌 {name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='ops-card-subtitle'>{desc}</div>", unsafe_allow_html=True)

            is_connected = state["status"] == "Connected"
            status_color = "#16a34a" if is_connected else "#dc2626"
            st.markdown(
                f"<span style='color:{status_color};font-weight:700;'>● {state['status']}</span> "
                f"&nbsp; <span style='color:#94a3b8;font-size:12px;'>Last sync: {state['last_sync'] or 'Never'}</span>",
                unsafe_allow_html=True,
            )

            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("Configure", key=f"cfg_{name}", use_container_width=True):
                    st.info(f"Configuration panel for {name} would open here (demo).")
            with b2:
                if st.button("Test Connection", key=f"test_{name}", use_container_width=True):
                    st.success(f"✅ Test connection to {name} succeeded (simulated).")
            with b3:
                toggle_label = "Disconnect" if is_connected else "Connect"
                if st.button(toggle_label, key=f"toggle_{name}", use_container_width=True):
                    new_status = "Disconnected" if is_connected else "Connected"
                    st.session_state.integration_status[name] = {
                        "status": new_status,
                        "last_sync": datetime.now().strftime("%Y-%m-%d %H:%M") if new_status == "Connected" else state["last_sync"],
                    }
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.caption("This is a demo application — no real external secrets or connections are stored or made.")
