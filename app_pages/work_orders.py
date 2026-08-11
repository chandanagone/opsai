"""Work Orders page: full CRUD, filters, export."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from components.styles import page_header
from components.cards import kpi_row
from utils.constants import WORK_ORDER_STATUSES, PRIORITIES, FACILITIES
from utils.helpers import status_badge, priority_badge, today_str
from utils.export_utils import df_to_csv_bytes
from services import work_order_service as wo_service


def render(data: dict):
    assets = data["assets"]
    page_header("Work Orders", "Create, track, and resolve maintenance and operations work orders.")

    df = wo_service.get_work_orders()

    kpi_row([
        {"label": "Total Work Orders", "value": len(df)},
        {"label": "Open", "value": int((df["Status"] == "Open").sum()) if not df.empty else 0},
        {"label": "In Progress", "value": int((df["Status"] == "In Progress").sum()) if not df.empty else 0},
        {"label": "Completed", "value": int((df["Status"] == "Completed").sum()) if not df.empty else 0},
        {"label": "Overdue", "value": len(wo_service.get_overdue(df))},
    ])

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)

    with st.expander("➕ Create New Work Order"):
        with st.form("create_wo_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                title = st.text_input("Title *")
                facility = st.selectbox("Facility *", FACILITIES)
                category = st.selectbox("Category", ["HVAC", "Electrical", "Plumbing", "Fire Safety",
                                                       "Security", "General Maintenance", "Elevator", "Cleaning"])
            with c2:
                asset_id = st.selectbox("Asset ID", [""] + (assets["Asset_ID"].tolist() if not assets.empty else []))
                location = st.text_input("Location", value="Floor 1 - Zone A")
                priority = st.selectbox("Priority *", PRIORITIES)
            with c3:
                technician = st.text_input("Assigned Technician")
                due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=7))
                est_cost = st.number_input("Estimated Cost", min_value=0.0, value=500.0, step=50.0)
            description = st.text_area("Description")

            submitted = st.form_submit_button("Create Work Order", use_container_width=True)
            if submitted:
                if not title or not facility or not priority:
                    st.error("Please fill all required fields marked with *.")
                else:
                    new_id = wo_service.create_work_order({
                        "Title": title, "Description": description, "Facility": facility,
                        "Location": location, "Asset_ID": asset_id, "Category": category,
                        "Priority": priority, "Status": "Open", "Assigned_Technician": technician or "Unassigned",
                        "Due_Date": due_date.strftime("%Y-%m-%d"), "Estimated_Cost": est_cost,
                    })
                    st.success(f"✅ Work order {new_id} created.")
                    st.rerun()

    # ---- Filters ----
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        status_f = st.multiselect("Status", WORK_ORDER_STATUSES, key="wo_status_filter")
    with f2:
        priority_f = st.multiselect("Priority", PRIORITIES, key="wo_priority_filter")
    with f3:
        facility_f = st.multiselect("Facility", FACILITIES, key="wo_facility_filter")
    with f4:
        tech_options = sorted(df["Assigned_Technician"].dropna().unique().tolist()) if not df.empty else []
        tech_f = st.multiselect("Technician", tech_options, key="wo_tech_filter")
    with f5:
        search = st.text_input("Search title", key="wo_search")

    filtered = df.copy()
    if status_f:
        filtered = filtered[filtered["Status"].isin(status_f)]
    if priority_f:
        filtered = filtered[filtered["Priority"].isin(priority_f)]
    if facility_f:
        filtered = filtered[filtered["Facility"].isin(facility_f)]
    if tech_f:
        filtered = filtered[filtered["Assigned_Technician"].isin(tech_f)]
    if search:
        filtered = filtered[filtered["Title"].str.contains(search, case=False, na=False)]

    show_overdue = st.checkbox("Show only overdue work orders", key="wo_overdue_only")
    if show_overdue:
        filtered = wo_service.get_overdue(filtered)

    st.markdown(f"**{len(filtered)}** work order(s) match your filters")

    if filtered.empty:
        st.info("ℹ️ No work orders match the selected filters.")
    else:
        display_df = filtered.copy()
        st.dataframe(
            display_df[["Work_Order_ID", "Title", "Facility", "Category", "Priority", "Status",
                        "Assigned_Technician", "Due_Date", "Estimated_Cost"]],
            use_container_width=True, hide_index=True, height=320,
        )

        st.download_button("⬇️ Export Filtered to CSV", data=df_to_csv_bytes(filtered),
                            file_name="work_orders_export.csv", mime="text/csv")

        st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)
        st.markdown("#### Manage a Work Order")
        selected_id = st.selectbox("Select Work Order ID", filtered["Work_Order_ID"].tolist(), key="wo_manage_select")
        row = df[df["Work_Order_ID"] == selected_id].iloc[0]

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            new_status = st.selectbox("Change Status", WORK_ORDER_STATUSES,
                                       index=WORK_ORDER_STATUSES.index(row["Status"]) if row["Status"] in WORK_ORDER_STATUSES else 0,
                                       key="wo_status_change")
            if st.button("Update Status", key="wo_update_status_btn"):
                wo_service.change_status(selected_id, new_status)
                st.success(f"Status updated to {new_status}.")
                st.rerun()
        with m2:
            new_tech = st.text_input("Reassign Technician", value=row["Assigned_Technician"], key="wo_reassign_tech")
            if st.button("Assign Technician", key="wo_assign_btn"):
                wo_service.assign_technician(selected_id, new_tech)
                st.success("Technician assigned.")
                st.rerun()
        with m3:
            new_actual = st.number_input("Actual Cost", min_value=0.0,
                                          value=float(row["Actual_Cost"]) if not pd.isna(row["Actual_Cost"]) else 0.0,
                                          key="wo_actual_cost")
            if st.button("Update Cost", key="wo_update_cost_btn"):
                wo_service.update_work_order(selected_id, {"Actual_Cost": new_actual})
                st.success("Cost updated.")
                st.rerun()
        with m4:
            st.write("")
            confirm_delete = st.checkbox("Confirm delete", key="wo_confirm_delete")
            if st.button("🗑️ Delete Work Order", key="wo_delete_btn", disabled=not confirm_delete):
                wo_service.delete_work_order(selected_id)
                st.success(f"Work order {selected_id} deleted.")
                st.rerun()
