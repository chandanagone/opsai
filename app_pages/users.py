"""Users page: user administration with CRUD and validation."""

import streamlit as st
import pandas as pd

from components.styles import page_header
from utils.constants import USER_ROLES, FACILITIES
from utils.validators import is_valid_email, is_valid_phone, is_non_empty, duplicate_email_exists
from utils.helpers import generate_id, today_str
from utils.export_utils import df_to_csv_bytes
from services import data_service

SESSION_KEY = "users_dataframe"


def _get_users():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = data_service.load_users().copy()
    return st.session_state[SESSION_KEY]


def _persist():
    data_service.save_dataframe("users", st.session_state[SESSION_KEY])


def render(data: dict):
    page_header("Users", "Manage user accounts, roles, and access across the platform.")

    df = _get_users()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Users", len(df))
    k2.metric("Active", int((df["Status"] == "Active").sum()) if not df.empty else 0)
    k3.metric("Inactive", int((df["Status"] == "Inactive").sum()) if not df.empty else 0)
    k4.metric("Administrators", int((df["Role"] == "Administrator").sum()) if not df.empty else 0)

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)

    with st.expander("➕ Add New User"):
        with st.form("create_user_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                full_name = st.text_input("Full Name *")
                email = st.text_input("Email *")
            with c2:
                role = st.selectbox("Role *", USER_ROLES)
                facility = st.selectbox("Facility", FACILITIES)
            with c3:
                department = st.text_input("Department", value="Facilities")
                phone = st.text_input("Phone Number", value="+91-9000000000")

            if st.form_submit_button("Add User", use_container_width=True):
                errors = []
                if not is_non_empty(full_name):
                    errors.append("Full name is required.")
                if not is_valid_email(email):
                    errors.append("A valid email address is required.")
                elif duplicate_email_exists(df, email):
                    errors.append("A user with this email already exists.")
                if not is_valid_phone(phone):
                    errors.append("Please enter a valid phone number.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    new_id = generate_id("USR", df["User_ID"].tolist() if not df.empty else [], width=3)
                    new_row = pd.DataFrame([{
                        "User_ID": new_id, "Full_Name": full_name, "Email": email, "Role": role,
                        "Facility": facility, "Department": department, "Phone_Number": phone,
                        "Status": "Active", "Last_Login": "", "Created_Date": today_str(),
                    }])
                    st.session_state[SESSION_KEY] = pd.concat([df, new_row], ignore_index=True)
                    _persist()
                    st.success(f"✅ User {new_id} added.")
                    st.rerun()

    f1, f2, f3 = st.columns(3)
    with f1:
        role_f = st.multiselect("Role", USER_ROLES, key="user_role_filter")
    with f2:
        status_f = st.multiselect("Status", ["Active", "Inactive"], key="user_status_filter")
    with f3:
        search = st.text_input("Search name or email", key="user_search")

    filtered = df.copy()
    if role_f:
        filtered = filtered[filtered["Role"].isin(role_f)]
    if status_f:
        filtered = filtered[filtered["Status"].isin(status_f)]
    if search:
        filtered = filtered[
            filtered["Full_Name"].str.contains(search, case=False, na=False)
            | filtered["Email"].str.contains(search, case=False, na=False)
        ]

    st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
    st.markdown("<div class='ops-card-title'>User Directory</div>", unsafe_allow_html=True)
    if filtered.empty:
        st.info("ℹ️ No users match the selected filters.")
    else:
        st.dataframe(
            filtered[["User_ID", "Full_Name", "Email", "Role", "Facility", "Department", "Status", "Last_Login"]],
            use_container_width=True, hide_index=True, height=320,
        )
        st.download_button("⬇️ Export Users to CSV", data=df_to_csv_bytes(filtered),
                            file_name="users_export.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

    if not filtered.empty:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Manage User</div>", unsafe_allow_html=True)
        selected_id = st.selectbox("Select User", filtered["User_ID"].tolist(), key="user_manage_select")
        row = df[df["User_ID"] == selected_id].iloc[0]

        a1, a2, a3 = st.columns(3)
        with a1:
            new_status = "Inactive" if row["Status"] == "Active" else "Active"
            if st.button(f"{'🚫 Deactivate' if row['Status']=='Active' else '✅ Activate'}", key="user_toggle_status", use_container_width=True):
                mask = df["User_ID"] == selected_id
                st.session_state[SESSION_KEY].loc[mask, "Status"] = new_status
                _persist()
                st.success(f"User set to {new_status}.")
                st.rerun()
        with a2:
            new_role = st.selectbox("Change Role", USER_ROLES,
                                     index=USER_ROLES.index(row["Role"]) if row["Role"] in USER_ROLES else 0,
                                     key="user_role_change")
            if st.button("Update Role", key="user_update_role_btn", use_container_width=True):
                mask = df["User_ID"] == selected_id
                st.session_state[SESSION_KEY].loc[mask, "Role"] = new_role
                _persist()
                st.success("Role updated.")
                st.rerun()
        with a3:
            confirm = st.checkbox("Confirm delete", key="user_confirm_delete")
            if st.button("🗑️ Delete User", key="user_delete_btn", disabled=not confirm, use_container_width=True):
                st.session_state[SESSION_KEY] = df[df["User_ID"] != selected_id].reset_index(drop=True)
                _persist()
                st.success("User deleted.")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
