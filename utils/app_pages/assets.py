"""Assets page: registry, CRUD, detail panel, maintenance/work-order history."""

import streamlit as st
import pandas as pd
from datetime import datetime

from components.styles import page_header
from components.cards import kpi_row
from components.charts import bar_chart
from utils.constants import ASSET_STATUSES, FACILITIES
from utils.export_utils import df_to_csv_bytes
from utils.helpers import safe_mean
from services import asset_service


def render(data: dict):
    work_orders = data["work_orders"]
    maintenance = data["maintenance_history"]

    page_header("Assets", "Register, track, and maintain the health of every facility asset.")

    df = asset_service.get_assets()

    kpi_row([
        {"label": "Total Assets", "value": len(df)},
        {"label": "Operational", "value": int((df["Operating_Status"] == "Operational").sum()) if not df.empty else 0},
        {"label": "Critical", "value": int((df["Operating_Status"] == "Critical").sum()) if not df.empty else 0},
        {"label": "Avg Health Score", "value": f"{safe_mean(df['Health_Score']):.0f}%" if not df.empty else "0%"},
    ])

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)

    with st.expander("➕ Register New Asset"):
        with st.form("create_asset_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                name = st.text_input("Asset Name *")
                asset_type = st.text_input("Asset Type *", value="HVAC Chiller")
                facility = st.selectbox("Facility *", FACILITIES)
            with c2:
                manufacturer = st.text_input("Manufacturer")
                model = st.text_input("Model")
                serial = st.text_input("Serial Number")
            with c3:
                responsible = st.text_input("Responsible Person")
                health = st.slider("Health Score", 0, 100, 85)
                status = st.selectbox("Operating Status", ASSET_STATUSES)
            location = st.text_input("Location", value="Floor 1 - Zone A")

            if st.form_submit_button("Register Asset", use_container_width=True):
                if not name or not asset_type or not facility:
                    st.error("Please fill all required fields marked with *.")
                else:
                    new_id = asset_service.create_asset({
                        "Asset_Name": name, "Asset_Type": asset_type, "Facility": facility,
                        "Location": location, "Manufacturer": manufacturer, "Model": model,
                        "Serial_Number": serial, "Next_Maintenance_Date": datetime.now().strftime("%Y-%m-%d"),
                        "Health_Score": health, "Operating_Status": status,
                        "Energy_Consumption_kWh": 0.0, "Responsible_Person": responsible or "Unassigned",
                    })
                    st.success(f"✅ Asset {new_id} registered.")
                    st.rerun()

    # ---- Filters ----
    f1, f2, f3 = st.columns(3)
    with f1:
        facility_f = st.multiselect("Facility", FACILITIES, key="asset_facility_filter")
    with f2:
        status_f = st.multiselect("Status", ASSET_STATUSES, key="asset_status_filter")
    with f3:
        search = st.text_input("Search asset name", key="asset_search")

    filtered = df.copy()
    if facility_f:
        filtered = filtered[filtered["Facility"].isin(facility_f)]
    if status_f:
        filtered = filtered[filtered["Operating_Status"].isin(status_f)]
    if search:
        filtered = filtered[filtered["Asset_Name"].str.contains(search, case=False, na=False)]

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Asset Registry</div>", unsafe_allow_html=True)
        if filtered.empty:
            st.info("ℹ️ No assets match the selected filters.")
        else:
            st.dataframe(
                filtered[["Asset_ID", "Asset_Name", "Facility", "Operating_Status", "Health_Score", "Next_Maintenance_Date"]],
                use_container_width=True, hide_index=True, height=320,
            )
            st.download_button("⬇️ Export Assets to CSV", data=df_to_csv_bytes(filtered),
                                file_name="assets_export.csv", mime="text/csv")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
        st.markdown("<div class='ops-card-title'>Asset Health Distribution</div>", unsafe_allow_html=True)
        if not filtered.empty:
            dist = filtered["Operating_Status"].value_counts().reset_index()
            dist.columns = ["Status", "Count"]
            st.plotly_chart(bar_chart(dist, "Status", "Count"), use_container_width=True)
        else:
            st.plotly_chart(bar_chart(pd.DataFrame(), "x", "y"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if not filtered.empty:
        st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)
        st.markdown("#### Asset Details")
        selected_id = st.selectbox("Select Asset", filtered["Asset_ID"].tolist(), key="asset_detail_select")
        row = df[df["Asset_ID"] == selected_id].iloc[0]

        d1, d2 = st.columns([1.2, 1])
        with d1:
            st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
            st.write(f"**Name:** {row['Asset_Name']}")
            st.write(f"**Type:** {row['Asset_Type']}  |  **Facility:** {row['Facility']}")
            st.write(f"**Manufacturer:** {row['Manufacturer']}  |  **Model:** {row['Model']}")
            st.write(f"**Serial:** {row['Serial_Number']}")
            st.write(f"**Installed:** {row['Installation_Date']}  |  **Next Maintenance:** {row['Next_Maintenance_Date']}")
            st.progress(int(row["Health_Score"]) / 100, text=f"Health score: {row['Health_Score']}%")

            e1, e2 = st.columns(2)
            with e1:
                new_status = st.selectbox("Update Status", ASSET_STATUSES,
                                           index=ASSET_STATUSES.index(row["Operating_Status"]) if row["Operating_Status"] in ASSET_STATUSES else 0,
                                           key="asset_status_update")
                if st.button("Save Status", key="asset_save_status"):
                    asset_service.update_asset(selected_id, {"Operating_Status": new_status})
                    st.success("Status updated.")
                    st.rerun()
            with e2:
                confirm = st.checkbox("Confirm delete", key="asset_confirm_delete")
                if st.button("🗑️ Delete Asset", key="asset_delete_btn", disabled=not confirm):
                    asset_service.delete_asset(selected_id)
                    st.success("Asset deleted.")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with d2:
            st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
            st.markdown("**Work Order History**")
            wo_hist = asset_service.get_asset_work_orders(selected_id, work_orders)
            if not wo_hist.empty:
                st.dataframe(wo_hist[["Work_Order_ID", "Title", "Status"]], hide_index=True, use_container_width=True)
            else:
                st.caption("No work orders recorded for this asset.")
            st.markdown("**Maintenance History**")
            maint_hist = asset_service.get_asset_maintenance_history(selected_id, maintenance)
            if not maint_hist.empty:
                st.dataframe(maint_hist[["Date", "Maintenance_Type", "Technician"]], hide_index=True, use_container_width=True)
            else:
                st.caption("No maintenance history recorded for this asset.")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='ops-card'>", unsafe_allow_html=True)
    st.markdown("<div class='ops-card-title'>Upcoming Maintenance (next 30 days)</div>", unsafe_allow_html=True)
    upcoming = asset_service.upcoming_maintenance(df)
    if not upcoming.empty:
        st.dataframe(upcoming[["Asset_ID", "Asset_Name", "Facility", "Next_Maintenance_Date"]],
                     hide_index=True, use_container_width=True)
    else:
        st.info("ℹ️ No assets due for maintenance in the next 30 days.")
    st.markdown("</div>", unsafe_allow_html=True)
