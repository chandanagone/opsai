"""Settings page: general, notifications, energy, maintenance, security, data, appearance."""

import streamlit as st
import os
import json
from datetime import datetime

from components.styles import page_header
from services import data_service
from services import authentication_service as auth

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "app_settings.json")

DEFAULT_SETTINGS = {
    "organization_name": "FacilityOps Inc.",
    "default_facility": "Corporate HQ - Tower A",
    "timezone": "Asia/Kolkata",
    "date_format": "YYYY-MM-DD",
    "currency": "INR (₹)",
    "units": "Metric",
    "email_notifications": True,
    "sms_notifications": False,
    "critical_alert_notifications": True,
    "daily_summary": True,
    "weekly_report": True,
    "energy_target": 2500,
    "peak_hour_threshold": 3000,
    "warning_threshold": 2800,
    "carbon_emission_factor": 0.71,
    "default_wo_priority": "Medium",
    "preventive_interval_days": 90,
    "overdue_reminder_days": 3,
    "auto_assignment": False,
    "session_timeout_min": 30,
    "failed_login_limit": 5,
    "password_min_length": 8,
    "two_factor_demo": False,
    "theme": "Light",
    "layout_density": "Comfortable",
    "card_density": "Standard",
}


def _load_settings():
    if "app_settings" not in st.session_state:
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r") as f:
                    saved = json.load(f)
                merged = {**DEFAULT_SETTINGS, **saved}
            else:
                merged = DEFAULT_SETTINGS.copy()
        except Exception:
            merged = DEFAULT_SETTINGS.copy()
        st.session_state.app_settings = merged
    return st.session_state.app_settings


def _save_settings(settings: dict):
    try:
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as exc:
        st.error(f"Could not save settings: {exc}")
        return False


def render(data: dict):
    page_header("Settings", "Configure organization, notification, energy, maintenance, and security preferences.")

    settings = _load_settings()

    tabs = st.tabs(["General", "Notifications", "Energy", "Maintenance", "Security", "Data Management", "Appearance"])

    with tabs[0]:
        settings["organization_name"] = st.text_input("Organization Name", settings["organization_name"])
        settings["default_facility"] = st.selectbox(
            "Default Facility", ["Corporate HQ - Tower A", "North Distribution Center", "Riverside Campus"],
            index=["Corporate HQ - Tower A", "North Distribution Center", "Riverside Campus"].index(settings["default_facility"])
            if settings["default_facility"] in ["Corporate HQ - Tower A", "North Distribution Center", "Riverside Campus"] else 0,
        )
        settings["timezone"] = st.selectbox("Time Zone", ["Asia/Kolkata", "UTC", "America/New_York", "Europe/London"],
                                             index=["Asia/Kolkata", "UTC", "America/New_York", "Europe/London"].index(settings["timezone"]) if settings["timezone"] in ["Asia/Kolkata", "UTC", "America/New_York", "Europe/London"] else 0)
        settings["date_format"] = st.selectbox("Date Format", ["YYYY-MM-DD", "DD-MM-YYYY", "MM/DD/YYYY"],
                                                index=["YYYY-MM-DD", "DD-MM-YYYY", "MM/DD/YYYY"].index(settings["date_format"]) if settings["date_format"] in ["YYYY-MM-DD", "DD-MM-YYYY", "MM/DD/YYYY"] else 0)
        settings["currency"] = st.selectbox("Currency", ["INR (₹)", "USD ($)", "EUR (€)"],
                                             index=["INR (₹)", "USD ($)", "EUR (€)"].index(settings["currency"]) if settings["currency"] in ["INR (₹)", "USD ($)", "EUR (€)"] else 0)
        settings["units"] = st.selectbox("Measurement Units", ["Metric", "Imperial"],
                                          index=["Metric", "Imperial"].index(settings["units"]) if settings["units"] in ["Metric", "Imperial"] else 0)

    with tabs[1]:
        settings["email_notifications"] = st.toggle("Email Notifications", settings["email_notifications"])
        settings["sms_notifications"] = st.toggle("SMS Notifications", settings["sms_notifications"])
        settings["critical_alert_notifications"] = st.toggle("Critical Alert Notifications", settings["critical_alert_notifications"])
        settings["daily_summary"] = st.toggle("Daily Summary", settings["daily_summary"])
        settings["weekly_report"] = st.toggle("Weekly Report", settings["weekly_report"])

    with tabs[2]:
        settings["energy_target"] = st.number_input("Energy Target (kWh/day)", min_value=0, value=int(settings["energy_target"]))
        settings["peak_hour_threshold"] = st.number_input("Peak Hour Threshold (kWh)", min_value=0, value=int(settings["peak_hour_threshold"]))
        settings["warning_threshold"] = st.number_input("Warning Threshold (kWh)", min_value=0, value=int(settings["warning_threshold"]))
        settings["carbon_emission_factor"] = st.number_input("Carbon Emission Factor (kgCO2/kWh)", min_value=0.0, value=float(settings["carbon_emission_factor"]), step=0.01)

    with tabs[3]:
        settings["default_wo_priority"] = st.selectbox("Default Work Order Priority", ["Low", "Medium", "High", "Critical"],
                                                         index=["Low", "Medium", "High", "Critical"].index(settings["default_wo_priority"]) if settings["default_wo_priority"] in ["Low", "Medium", "High", "Critical"] else 1)
        settings["preventive_interval_days"] = st.number_input("Preventive Maintenance Interval (days)", min_value=1, value=int(settings["preventive_interval_days"]))
        settings["overdue_reminder_days"] = st.number_input("Overdue Reminder Period (days)", min_value=1, value=int(settings["overdue_reminder_days"]))
        settings["auto_assignment"] = st.toggle("Auto-Assignment of Technicians", settings["auto_assignment"])

    with tabs[4]:
        settings["session_timeout_min"] = st.number_input("Session Timeout (minutes)", min_value=5, value=int(settings["session_timeout_min"]))
        settings["failed_login_limit"] = st.number_input("Failed Login Limit", min_value=1, value=int(settings["failed_login_limit"]))
        settings["password_min_length"] = st.number_input("Password Minimum Length", min_value=6, value=int(settings["password_min_length"]))
        settings["two_factor_demo"] = st.toggle("Two-Factor Authentication (demo)", settings["two_factor_demo"])

        st.markdown("#### Change My Password")
        with st.form("change_my_password_form", clear_on_submit=True):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Update Password"):
                if new_password != confirm_password:
                    st.error("New password and confirmation do not match.")
                else:
                    ok, message = auth.change_password(
                        st.session_state.get("auth_username", ""), current_password, new_password
                    )
                    if ok:
                        st.success(message)
                    else:
                        st.error(message)

    with tabs[5]:
        st.markdown("**Data File Status**")
        for key, label in [("work_orders", "Work Orders"), ("assets", "Assets"), ("alerts", "Alerts"),
                            ("users", "Users"), ("energy_history", "Energy History"),
                            ("maintenance_history", "Maintenance History"), ("integrations", "Integrations")]:
            loader = getattr(data_service, f"load_{key}")
            df = loader()
            st.write(f"- {label}: **{len(df)}** records {'✅' if not df.empty else '⚠️ empty'}")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("📤 Export All Data", use_container_width=True):
                st.success("Use the Export buttons on each module page (Work Orders, Assets, Alerts, Users) to download individual CSV files.")
        with c2:
            if st.button("♻️ Reset Demo Data", use_container_width=True):
                import generate_data
                generate_data.generate_all(force=True)
                data_service.clear_cache()
                for k in ["wo_dataframe", "asset_dataframe", "alert_dataframe", "users_dataframe"]:
                    st.session_state.pop(k, None)
                st.success("Demo data has been reset.")
                st.rerun()
        with c3:
            if st.button("💾 Create Local Backup", use_container_width=True):
                backup_dir = os.path.join(BASE_DIR, "data", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                try:
                    import shutil
                    shutil.copytree(os.path.join(BASE_DIR, "data"), backup_dir,
                                     ignore=shutil.ignore_patterns("backup_*"))
                    st.success(f"Backup created at data/{os.path.basename(backup_dir)}")
                except Exception as exc:
                    st.error(f"Backup failed: {exc}")

    with tabs[6]:
        settings["theme"] = st.selectbox("Theme Preference", ["Light", "Dark (preview only)"],
                                          index=["Light", "Dark (preview only)"].index(settings["theme"]) if settings["theme"] in ["Light", "Dark (preview only)"] else 0)
        settings["layout_density"] = st.selectbox("Layout Density", ["Comfortable", "Compact"],
                                                   index=["Comfortable", "Compact"].index(settings["layout_density"]) if settings["layout_density"] in ["Comfortable", "Compact"] else 0)
        settings["card_density"] = st.selectbox("Dashboard Card Density", ["Standard", "Dense"],
                                                 index=["Standard", "Dense"].index(settings["card_density"]) if settings["card_density"] in ["Standard", "Dense"] else 0)

    st.markdown("<div class='ops-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Settings", use_container_width=True, type="primary"):
        st.session_state.app_settings = settings
        if _save_settings(settings):
            st.success("✅ Settings saved.")
