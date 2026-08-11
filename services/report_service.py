"""Report service: builds report data payloads and tracks report generation history."""

import pandas as pd
import streamlit as st

from utils.helpers import now_str, safe_sum, safe_mean
from utils.export_utils import build_html_report

REPORT_TYPES = [
    "Executive Summary Report",
    "Energy Consumption Report",
    "Work Order Report",
    "Asset Health Report",
    "Maintenance Performance Report",
    "Occupancy Report",
    "Security Incident Report",
    "Cost Savings Report",
    "User Activity Report",
]

HISTORY_KEY = "report_history"


def _history() -> list:
    if HISTORY_KEY not in st.session_state:
        st.session_state[HISTORY_KEY] = []
    return st.session_state[HISTORY_KEY]


def log_report_generated(report_type: str, facility: str, date_range: str):
    _history().insert(0, {
        "Report": report_type,
        "Facility": facility,
        "Date Range": date_range,
        "Generated At": now_str(),
    })


def get_report_history() -> pd.DataFrame:
    hist = _history()
    if not hist:
        return pd.DataFrame(columns=["Report", "Facility", "Date Range", "Generated At"])
    return pd.DataFrame(hist)


def build_report(report_type: str, facility: str, date_range_label: str,
                  work_orders: pd.DataFrame, assets: pd.DataFrame, alerts: pd.DataFrame,
                  energy: pd.DataFrame, maintenance: pd.DataFrame, users: pd.DataFrame,
                  original_metrics: pd.DataFrame) -> str:
    """Returns full printable HTML string for the requested report type."""
    sections = []

    if report_type == "Executive Summary Report":
        kpis = {
            "Open Work Orders": int((work_orders["Status"].isin(["Open", "Assigned", "In Progress"])).sum()) if not work_orders.empty else 0,
            "Active Assets": int((assets["Operating_Status"] == "Operational").sum()) if not assets.empty else 0,
            "Critical Alerts": int((alerts["Severity"] == "Critical").sum()) if not alerts.empty else 0,
            "Avg Energy (kWh/day)": safe_mean(energy["Energy_Usage_kWh"]) if not energy.empty else 0,
        }
        sections.append({"heading": "Key Performance Indicators", "type": "kpi", "data": kpis})
        sections.append({"heading": "Recent Work Orders", "type": "table", "data": work_orders.head(10)})
        sections.append({"heading": "Recent Alerts", "type": "table", "data": alerts.head(10)})

    elif report_type == "Energy Consumption Report":
        kpis = {
            "Total Energy (kWh)": safe_sum(energy["Energy_Usage_kWh"]) if not energy.empty else 0,
            "Avg Daily Energy (kWh)": safe_mean(energy["Energy_Usage_kWh"]) if not energy.empty else 0,
            "Total Cost": safe_sum(energy["Cost_INR"]) if not energy.empty else 0,
        }
        sections.append({"heading": "Energy KPIs", "type": "kpi", "data": kpis})
        sections.append({"heading": "Energy History", "type": "table", "data": energy.head(60)})

    elif report_type == "Work Order Report":
        sections.append({"heading": "All Work Orders", "type": "table", "data": work_orders})

    elif report_type == "Asset Health Report":
        sections.append({"heading": "Asset Inventory & Health", "type": "table", "data": assets})

    elif report_type == "Maintenance Performance Report":
        sections.append({"heading": "Maintenance History", "type": "table", "data": maintenance})

    elif report_type == "Occupancy Report":
        cols = [c for c in original_metrics.columns if "Space" in c or "Day" in c]
        sections.append({"heading": "Space Utilization Trend", "type": "table",
                          "data": original_metrics[cols] if cols else original_metrics})

    elif report_type == "Security Incident Report":
        sec_alerts = alerts[alerts["Category"] == "Security"] if not alerts.empty else alerts
        sections.append({"heading": "Security Alerts", "type": "table", "data": sec_alerts})

    elif report_type == "Cost Savings Report":
        kpis = {
            "Estimated WO Cost": safe_sum(work_orders["Estimated_Cost"]) if not work_orders.empty else 0,
            "Actual WO Cost": safe_sum(work_orders["Actual_Cost"]) if not work_orders.empty else 0,
        }
        sections.append({"heading": "Cost Overview", "type": "kpi", "data": kpis})
        sections.append({"heading": "Work Order Costs", "type": "table",
                          "data": work_orders[["Work_Order_ID", "Title", "Estimated_Cost", "Actual_Cost"]] if not work_orders.empty else work_orders})

    elif report_type == "User Activity Report":
        sections.append({"heading": "User Directory", "type": "table",
                          "data": users.drop(columns=[c for c in ["Password"] if c in users.columns]) if not users.empty else users})

    else:
        sections.append({"heading": "Report", "type": "text", "data": "No content available."})

    html = build_html_report(
        title=report_type,
        subtitle=f"Facility: {facility} | Date range: {date_range_label}",
        sections=sections,
    )
    log_report_generated(report_type, facility, date_range_label)
    return html
