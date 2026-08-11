"""
generate_data.py
-----------------
One-time / idempotent generator for realistic sample data used by the
enhanced FacilityOps AI application. Run directly (python generate_data.py)
or import `generate_all()` from services/data_service.py.

This script NEVER touches facility_data.csv (the original data file).
It only writes into the local ./data folder.
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

FACILITIES = ["Corporate HQ - Tower A", "North Distribution Center", "Riverside Campus"]
DEPARTMENTS = ["Facilities", "IT", "Security", "Operations", "HR", "Finance"]

ASSET_TYPES = [
    "HVAC Chiller", "Air Handling Unit", "Elevator", "Generator", "Fire Pump",
    "Boiler", "Transformer", "CCTV Camera", "Access Control Panel", "UPS System",
    "Water Pump", "Escalator", "Cooling Tower", "Lighting Panel", "Compressor",
]

MANUFACTURERS = ["Carrier", "Trane", "Siemens", "Honeywell", "Johnson Controls",
                  "Schneider Electric", "ABB", "Otis", "Daikin", "Bosch"]

WORK_ORDER_CATEGORIES = ["HVAC", "Electrical", "Plumbing", "Fire Safety",
                          "Security", "General Maintenance", "Elevator", "Cleaning"]

TECHNICIANS = ["Ravi Kumar", "Anita Sharma", "John Mathews", "Priya Nair",
               "David Chen", "Sara Ali", "Michael Rodriguez", "Fatima Khan"]

STATUSES_WO = ["Open", "Assigned", "In Progress", "On Hold", "Completed", "Cancelled"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]

ASSET_STATUSES = ["Operational", "Warning", "Maintenance", "Offline", "Critical"]

ALERT_CATEGORIES = ["Energy", "Maintenance", "Security", "Occupancy", "Asset", "System"]
SEVERITIES = ["Information", "Warning", "High", "Critical"]
ALERT_STATUSES = ["New", "Acknowledged", "Assigned", "Resolved", "Reopened"]

ROLES = ["Administrator", "Facility Manager", "Maintenance Manager",
         "Technician", "Security Officer", "Analyst", "Viewer"]


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _rand_date(days_back_min, days_back_max):
    days_back = random.randint(days_back_min, days_back_max)
    return (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")


def generate_assets(n=24):
    rows = []
    for i in range(1, n + 1):
        asset_id = f"AST-{i:04d}"
        install_date = _rand_date(200, 2200)
        last_maint = _rand_date(1, 120)
        next_maint = (datetime.now() + timedelta(days=random.randint(-10, 90))).strftime("%Y-%m-%d")
        health = max(5, min(100, int(np.random.normal(78, 16))))
        if health < 35:
            status = "Critical"
        elif health < 55:
            status = "Warning"
        elif health < 65 and random.random() < 0.3:
            status = "Maintenance"
        else:
            status = random.choices(
                ["Operational", "Warning", "Offline"], weights=[85, 10, 5]
            )[0]
        rows.append({
            "Asset_ID": asset_id,
            "Asset_Name": f"{random.choice(ASSET_TYPES)} #{i}",
            "Asset_Type": random.choice(ASSET_TYPES),
            "Facility": random.choice(FACILITIES),
            "Location": f"Floor {random.randint(1, 12)} - Zone {random.choice('ABCD')}",
            "Manufacturer": random.choice(MANUFACTURERS),
            "Model": f"MDL-{random.randint(1000,9999)}",
            "Serial_Number": f"SN{random.randint(100000,999999)}",
            "Installation_Date": install_date,
            "Last_Maintenance_Date": last_maint,
            "Next_Maintenance_Date": next_maint,
            "Health_Score": health,
            "Operating_Status": status,
            "Energy_Consumption_kWh": round(random.uniform(5, 450), 1),
            "Responsible_Person": random.choice(TECHNICIANS),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "assets.csv"), index=False)
    return df


def generate_work_orders(asset_ids, n=32):
    rows = []
    for i in range(1, n + 1):
        wo_id = f"WO-{i:05d}"
        created = _rand_date(1, 90)
        created_dt = datetime.strptime(created, "%Y-%m-%d")
        due_dt = created_dt + timedelta(days=random.randint(1, 21))
        status = random.choices(STATUSES_WO, weights=[20, 15, 20, 8, 30, 7])[0]
        completed = ""
        if status == "Completed":
            completed = (created_dt + timedelta(days=random.randint(1, 20))).strftime("%Y-%m-%d")
        est_cost = round(random.uniform(50, 5000), 2)
        actual_cost = round(est_cost * random.uniform(0.7, 1.4), 2) if status == "Completed" else 0.0
        rows.append({
            "Work_Order_ID": wo_id,
            "Title": f"{random.choice(WORK_ORDER_CATEGORIES)} service request #{i}",
            "Description": f"Routine or corrective {random.choice(WORK_ORDER_CATEGORIES).lower()} task raised for facility upkeep.",
            "Facility": random.choice(FACILITIES),
            "Location": f"Floor {random.randint(1, 12)} - Zone {random.choice('ABCD')}",
            "Asset_ID": random.choice(asset_ids),
            "Category": random.choice(WORK_ORDER_CATEGORIES),
            "Priority": random.choices(PRIORITIES, weights=[30, 35, 25, 10])[0],
            "Status": status,
            "Assigned_Technician": random.choice(TECHNICIANS),
            "Created_Date": created,
            "Due_Date": due_dt.strftime("%Y-%m-%d"),
            "Completion_Date": completed,
            "Estimated_Cost": est_cost,
            "Actual_Cost": actual_cost,
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "work_orders.csv"), index=False)
    return df


def generate_alerts(asset_ids, n=20):
    rows = []
    titles = {
        "Energy": ["Peak demand threshold exceeded", "Unusual overnight energy draw", "Meter reading anomaly"],
        "Maintenance": ["Preventive maintenance overdue", "Unexpected equipment vibration", "Filter replacement due"],
        "Security": ["Unauthorized access attempt", "Perimeter sensor triggered", "Badge reader offline"],
        "Occupancy": ["Occupancy exceeds safe capacity", "Zone left unoccupied unusually long", "Meeting room conflict detected"],
        "Asset": ["Asset health score dropped sharply", "Asset offline unexpectedly", "Serial number mismatch on scan"],
        "System": ["Sensor connectivity lost", "Data sync delayed", "Backup job failed"],
    }
    for i in range(1, n + 1):
        category = random.choice(ALERT_CATEGORIES)
        created = datetime.now() - timedelta(hours=random.randint(1, 24 * 20))
        status = random.choices(ALERT_STATUSES, weights=[25, 20, 20, 30, 5])[0]
        resolved = ""
        if status == "Resolved":
            resolved = (created + timedelta(hours=random.randint(1, 48))).strftime("%Y-%m-%d %H:%M")
        rows.append({
            "Alert_ID": f"ALT-{i:04d}",
            "Alert_Title": random.choice(titles[category]),
            "Description": f"Automated monitoring flagged a {category.lower()} condition requiring review.",
            "Category": category,
            "Severity": random.choices(SEVERITIES, weights=[25, 35, 25, 15])[0],
            "Facility": random.choice(FACILITIES),
            "Asset_ID": random.choice(asset_ids) if random.random() > 0.2 else "",
            "Created_Time": created.strftime("%Y-%m-%d %H:%M"),
            "Status": status,
            "Assigned_Person": random.choice(TECHNICIANS) if status != "New" else "",
            "Resolved_Time": resolved,
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "alerts.csv"), index=False)
    return df


def generate_users(n=12):
    first = ["Ravi", "Anita", "John", "Priya", "David", "Sara", "Michael", "Fatima",
             "Karan", "Meera", "Alex", "Nina"]
    last = ["Kumar", "Sharma", "Mathews", "Nair", "Chen", "Ali", "Rodriguez", "Khan",
            "Patel", "Iyer", "Brown", "Fischer"]
    rows = []
    used_emails = set()
    for i in range(1, n + 1):
        fn, ln = first[(i - 1) % len(first)], last[(i - 1) % len(last)]
        email = f"{fn.lower()}.{ln.lower()}@facilityops.com"
        while email in used_emails:
            email = f"{fn.lower()}.{ln.lower()}{i}@facilityops.com"
        used_emails.add(email)
        rows.append({
            "User_ID": f"USR-{i:03d}",
            "Full_Name": f"{fn} {ln}",
            "Email": email,
            "Role": ROLES[(i - 1) % len(ROLES)],
            "Facility": random.choice(FACILITIES),
            "Department": random.choice(DEPARTMENTS),
            "Phone_Number": f"+91-9{random.randint(100000000,999999999)}",
            "Status": random.choices(["Active", "Inactive"], weights=[85, 15])[0],
            "Last_Login": _rand_date(0, 30),
            "Created_Date": _rand_date(60, 900),
        })
    # Ensure the two demo accounts exist for reference
    rows[0]["Full_Name"] = "Admin Administrator"
    rows[0]["Email"] = "admin@facilityops.com"
    rows[0]["Role"] = "Administrator"
    rows[0]["Status"] = "Active"
    rows[1]["Full_Name"] = "Facility Manager"
    rows[1]["Email"] = "manager@facilityops.com"
    rows[1]["Role"] = "Facility Manager"
    rows[1]["Status"] = "Active"
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "users.csv"), index=False)
    return df


def generate_energy_history(days=45):
    rows = []
    base = 2200
    for d in range(days, 0, -1):
        date = (datetime.now() - timedelta(days=d)).strftime("%Y-%m-%d")
        for facility in FACILITIES:
            seasonal = 250 * np.sin(d / 7.0)
            noise = np.random.normal(0, 120)
            usage = max(400, base + seasonal + noise + (150 if facility == FACILITIES[1] else 0))
            cost = round(usage * 8.2, 2)  # INR per kWh approx
            rows.append({
                "Date": date,
                "Facility": facility,
                "Energy_Usage_kWh": round(usage, 1),
                "Cost_INR": cost,
                "Peak_Demand_kW": round(usage / 18 + random.uniform(-3, 5), 1),
                "Carbon_Emission_kgCO2": round(usage * 0.71, 1),
            })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "energy_history.csv"), index=False)
    return df


def generate_maintenance_history(asset_ids, n=18):
    rows = []
    for i in range(1, n + 1):
        date = _rand_date(1, 180)
        rows.append({
            "Record_ID": f"MH-{i:04d}",
            "Asset_ID": random.choice(asset_ids),
            "Facility": random.choice(FACILITIES),
            "Maintenance_Type": random.choice(["Preventive", "Corrective", "Inspection", "Emergency"]),
            "Date": date,
            "Technician": random.choice(TECHNICIANS),
            "Duration_Hours": round(random.uniform(0.5, 8), 1),
            "Cost_INR": round(random.uniform(500, 25000), 2),
            "Notes": "Scheduled service completed within expected parameters.",
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "maintenance_history.csv"), index=False)
    return df


def generate_integrations():
    integrations = [
        ("Building Management System", "Centralized control of HVAC, lighting and access systems."),
        ("IoT Sensor Gateway", "Ingests live telemetry from facility IoT sensors."),
        ("Energy Meter API", "Pulls interval energy consumption data from smart meters."),
        ("Email Notifications", "Sends alert and report emails to configured recipients."),
        ("SMS Notifications", "Sends critical alerts via SMS gateway."),
        ("Microsoft Teams", "Posts alerts and daily summaries to a Teams channel."),
        ("ERP System", "Synchronizes work orders and cost data with the ERP."),
        ("Weather Service", "Provides weather data used for energy forecasting."),
        ("Cloud Storage", "Backs up reports and exports to cloud storage."),
        ("REST API", "General purpose REST endpoint for third-party access."),
    ]
    rows = []
    for name, desc in integrations:
        connected = random.random() > 0.4
        rows.append({
            "Integration_Name": name,
            "Description": desc,
            "Status": "Connected" if connected else "Disconnected",
            "Last_Sync": _rand_date(0, 10) if connected else "",
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "integrations.csv"), index=False)
    return df


def generate_all(force=False):
    """Generate all sample data files if they do not already exist (or force=True)."""
    _ensure_dir()
    assets_path = os.path.join(DATA_DIR, "assets.csv")
    if force or not os.path.exists(assets_path):
        assets_df = generate_assets()
    else:
        assets_df = pd.read_csv(assets_path)
    asset_ids = assets_df["Asset_ID"].tolist()

    for fname, func in [
        ("work_orders.csv", lambda: generate_work_orders(asset_ids)),
        ("alerts.csv", lambda: generate_alerts(asset_ids)),
        ("users.csv", generate_users),
        ("energy_history.csv", generate_energy_history),
        ("maintenance_history.csv", lambda: generate_maintenance_history(asset_ids)),
        ("integrations.csv", generate_integrations),
    ]:
        path = os.path.join(DATA_DIR, fname)
        if force or not os.path.exists(path):
            func()

    return True


if __name__ == "__main__":
    generate_all(force=True)
    print("Sample data generated in:", DATA_DIR)
    for f in sorted(os.listdir(DATA_DIR)):
        print(" -", f)
