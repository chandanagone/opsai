"""Login screen for the enhanced application."""

import streamlit as st
from services import authentication_service as auth
from utils.constants import APP_NAME, APP_TAGLINE


def render_login():
    st.markdown(
        f"<h1 style='text-align:center;margin-top:60px;color:#0b192e;'>🏢 {APP_NAME}</h1>"
        f"<p style='text-align:center;color:#64748b;font-size:15px;'>{APP_TAGLINE}</p>",
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        with st.form("enhanced_login_form"):
            identifier = st.text_input("Username or Email", placeholder="admin or admin@facilityops.com")
            show_pw = st.checkbox("Show password", key="login_show_pw")
            password = st.text_input(
                "Password", type="default" if show_pw else "password", placeholder="••••••••"
            )
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted and auth.attempt_login(identifier, password):
                st.rerun()

        if st.session_state.get("login_error"):
            st.error(st.session_state.login_error)

        st.caption("Your password is verified against a PBKDF2-SHA256 hash; plaintext passwords are not stored in the app data.")
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Demo access (change before deployment)"):
            st.write("Administrator: `admin` / `admin123`")
            st.write("Facility Manager: `manager` / `manager123`")
            st.caption("Set FACILITYOPS_ADMIN_PASSWORD and FACILITYOPS_MANAGER_PASSWORD before the first run to override these bootstrap passwords.")
