# FacilityOps AI — Enhanced Edition

A production-style, modular upgrade of the original **Agentic Facility Ops AI**
Streamlit application. This enhanced version runs **completely separately**
from the original `app.py` and never modifies, renames, or deletes any of
the original project files.

---

## 1. What was NOT touched

- `app.py` — byte-for-byte identical to the original (verified by checksum).
- `facility_data.csv` — byte-for-byte identical to the original.
- `README.md` — untouched.

A full copy of these three original files is also kept in `backup_original/`
for reference.

The original app still runs exactly as before:

```
streamlit run app.py
```

---

## 2. Running the enhanced app

### Windows Command Prompt

```cmd
cd path\to\OpsAI-main
pip install -r requirements_enhanced.txt
streamlit run app_enhanced.py
```

### macOS / Linux

```bash
cd path/to/OpsAI-main
pip install -r requirements_enhanced.txt
streamlit run app_enhanced.py
```

The app opens at `http://localhost:8501`.

---

## 3. Authentication and demo login credentials

| Role              | Username  | Password    |
|-------------------|-----------|-------------|
| Administrator     | `admin`   | `admin123`  |
| Facility Manager  | `manager` | `manager123`|

Passwords are stored as salted PBKDF2-SHA256 hashes in `data/auth_users.json`; plaintext passwords are not persisted. The credential store is created on first run. Before first run, you can override the bootstrap passwords with the `FACILITYOPS_ADMIN_PASSWORD` and `FACILITYOPS_MANAGER_PASSWORD` environment variables. Failed logins are temporarily locked after repeated attempts, and page access is filtered by role.

---

## 4. Project structure

```
OpsAI-main/
├── app.py                     # ORIGINAL — untouched
├── facility_data.csv          # ORIGINAL — untouched
├── README.md                  # ORIGINAL — untouched
├── backup_original/           # Verbatim copy of the 3 original files
│
├── app_enhanced.py            # Enhanced app entry point
├── requirements_enhanced.txt
├── README_ENHANCED.md         # This file
├── generate_data.py           # Sample data generator (idempotent)
│
├── app_pages/                 # One module per sidebar page
│   ├── login.py, overview.py, dashboard.py, ai_agents.py, modules.py,
│   │   work_orders.py, assets.py, monitoring.py, analytics.py,
│   │   reports.py, alerts.py, users.py, integrations.py, settings.py
│
├── components/                 # Shared UI building blocks
│   ├── styles.py, sidebar.py, header.py, cards.py, charts.py,
│   │   tables.py, notifications.py
│
├── services/                   # Business logic / data access layer
│   ├── data_service.py, work_order_service.py, asset_service.py,
│   │   alert_service.py, report_service.py, authentication_service.py
│
├── utils/                       # Generic helpers
│   ├── constants.py, helpers.py, validators.py, export_utils.py
│
└── data/                        # Generated sample data (auto-created)
    ├── work_orders.csv, assets.csv, alerts.csv, users.csv,
    │   energy_history.csv, maintenance_history.csv, integrations.csv
```

> **Note on structure:** the requested folder was named `pages/`. It was
> renamed to `app_pages/` because Streamlit automatically treats any
> folder literally named `pages/` next to the entry-point script as its
> **built-in** multi-page navigation system, which produced a duplicate,
> conflicting navigation UI. Using `app_pages/` keeps a single, custom
> sidebar navigation system exactly as required, while preserving every
> other part of the requested structure.

---

## 5. Module overview

| Module | Purpose |
|---|---|
| **Overview** | Executive KPI summary, energy trend, work-order status, recent items, AI recommendations, quick actions. |
| **Dashboard** | Filterable operational dashboard: energy, maintenance, work-order priority, occupancy, cost savings, recent activity. |
| **AI Agents** | Four simulated agents (Energy, Maintenance, Occupancy, Security) with enable/disable, run-now, details, plus the rule-based AI Assistant chat box. |
| **Modules** | Enable/disable platform modules and jump directly to the related page. |
| **Work Orders** | Full CRUD: create, filter, search, reassign, change status, delete, export, overdue tracking. |
| **Assets** | Asset registry with CRUD, detail panel, maintenance/work-order history, health chart, upcoming maintenance list. |
| **Monitoring** | Simulated real-time sensor readings, thresholds, sensor status table, active anomalies, manual/auto refresh. |
| **Analytics** | Trend analysis across energy, maintenance, work orders, assets, security, with a linear-regression 7-day forecast. |
| **Reports** | Nine report types with preview, CSV download, and printable HTML export, plus a session report history. |
| **Alerts** | Alert triage: acknowledge, assign, resolve, reopen, with filters and export. |
| **Users** | User administration: add, edit role, activate/deactivate, delete, with email/phone validation. |
| **Integrations** | Ten integration cards with simulated connect/disconnect/test actions (no real secrets stored). |
| **Settings** | General, notifications, energy, maintenance, security, data management, and appearance preferences (saved to `data/app_settings.json`). |

---

## 6. Data

- The original `facility_data.csv` (Day / Energy_Usage_kWh / Work_Orders_Closed
  / Space_Utilization_Pct / Security_Events) continues to be read read-only
  and powers the Overview trend chart, Occupancy analysis, and the AI
  Assistant.
- All additional CSVs in `data/` are generated automatically the first time
  the app runs (via `generate_data.py`) and contain realistic, related sample
  records:
  - 24 assets, 32 work orders, 20 alerts, 12 users, 45 days × 3 facilities of
    energy history, and 18 maintenance-history records — across 3 named
    facilities with consistent IDs and cross-references.
- If any data file is missing, empty, or unreadable, the app safely
  regenerates the full sample dataset rather than crashing.

---

## 7. Dependency installation

```bash
pip install -r requirements_enhanced.txt
```

Requires: `streamlit`, `pandas`, `plotly`, `numpy`. No API keys, no external
services, and no internet connection are required.

---

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'components'` (or `services`, `utils`, `app_pages`) | Run the app from **inside** the `OpsAI-main` folder: `cd OpsAI-main` then `streamlit run app_enhanced.py`. |
| Blank / empty charts | This means the underlying CSV has no rows for the selected filter — this is expected safe behavior, not an error. Clear filters or use **Settings → Data Management → Reset Demo Data**. |
| Login fails | Passwords are case-sensitive. After 5 failed attempts, wait 60 seconds before retrying. For a fresh local demo, use the bootstrap credentials above. |
| Port already in use | Run `streamlit run app_enhanced.py --server.port 8502` (or any free port). |
| Data looks stale after editing a CSV directly | Go to **Settings → Data Management → Reset Demo Data**, or restart the app (caches are cleared automatically after in-app edits). |
| Windows `pip` not recognized | Use `python -m pip install -r requirements_enhanced.txt`. |

---

## 9. Verification performed

- Every `.py` file compiled successfully (`python -m py_compile`).
- Every one of the 13 sidebar pages was exercised end-to-end with
  Streamlit's `AppTest` harness and loaded with **zero exceptions**.
- The app was started with `streamlit run app_enhanced.py` and returned
  `HTTP 200` with no errors in the server log.
- `app.py` and `facility_data.csv` checksums were compared before and after
  development and are **identical**.
