"""Application-wide constants for FacilityOps AI Enhanced."""

APP_NAME = "FacilityOps AI"
APP_TAGLINE = "Agentic Facility Operations Management Platform"

# ---- Colors ----
COLOR_SIDEBAR = "#0b192e"
COLOR_SIDEBAR_ACTIVE = "#16324f"
COLOR_BG = "#f5f7fb"
COLOR_CARD = "#ffffff"
COLOR_PRIMARY = "#2563eb"
COLOR_SUCCESS = "#16a34a"
COLOR_WARNING = "#d97706"
COLOR_CRITICAL = "#dc2626"
COLOR_INFO = "#0284c7"
COLOR_TEXT = "#1e293b"
COLOR_MUTED = "#64748b"
COLOR_BORDER = "#e2e8f0"

# ---- Navigation ----
NAV_ITEMS = [
    ("Overview", "grid"),
    ("Dashboard", "speedometer"),
    ("AI Agents", "cpu"),
    ("Modules", "layers"),
    ("Work Orders", "clipboard"),
    ("Assets", "box"),
    ("Monitoring", "activity"),
    ("Analytics", "bar-chart"),
    ("Reports", "file-text"),
    ("Alerts", "bell"),
    ("Users", "users"),
    ("Integrations", "plug"),
    ("Settings", "settings"),
]

NAV_ICONS = {
    "Overview": "🏠",
    "Dashboard": "📊",
    "AI Agents": "🤖",
    "Modules": "🧩",
    "Work Orders": "🛠️",
    "Assets": "📦",
    "Monitoring": "📡",
    "Analytics": "📈",
    "Reports": "📄",
    "Alerts": "🚨",
    "Users": "👥",
    "Integrations": "🔌",
    "Settings": "⚙️",
}

# ---- Authentication credentials are managed by services/authentication_service.py ----

# ---- Enumerations ----
WORK_ORDER_STATUSES = ["Open", "Assigned", "In Progress", "On Hold", "Completed", "Cancelled"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
ASSET_STATUSES = ["Operational", "Warning", "Maintenance", "Offline", "Critical"]
ALERT_CATEGORIES = ["Energy", "Maintenance", "Security", "Occupancy", "Asset", "System"]
ALERT_SEVERITIES = ["Information", "Warning", "High", "Critical"]
ALERT_STATUSES = ["New", "Acknowledged", "Assigned", "Resolved", "Reopened"]
USER_ROLES = ["Administrator", "Facility Manager", "Maintenance Manager",
              "Technician", "Security Officer", "Analyst", "Viewer"]
FACILITIES = ["Corporate HQ - Tower A", "North Distribution Center", "Riverside Campus"]

STATUS_COLOR_MAP = {
    "Operational": COLOR_SUCCESS, "Active": COLOR_SUCCESS, "Connected": COLOR_SUCCESS,
    "Completed": COLOR_SUCCESS, "Resolved": COLOR_SUCCESS, "Enabled": COLOR_SUCCESS,
    "Open": COLOR_INFO, "Assigned": COLOR_INFO, "New": COLOR_INFO, "Acknowledged": COLOR_INFO,
    "In Progress": COLOR_PRIMARY,
    "Warning": COLOR_WARNING, "On Hold": COLOR_WARNING, "Maintenance": COLOR_WARNING,
    "Reopened": COLOR_WARNING,
    "Critical": COLOR_CRITICAL, "Offline": COLOR_CRITICAL, "Cancelled": COLOR_CRITICAL,
    "Inactive": COLOR_CRITICAL, "Disconnected": COLOR_CRITICAL, "Disabled": COLOR_CRITICAL,
}

PRIORITY_COLOR_MAP = {
    "Low": COLOR_SUCCESS,
    "Medium": COLOR_INFO,
    "High": COLOR_WARNING,
    "Critical": COLOR_CRITICAL,
}

SEVERITY_COLOR_MAP = {
    "Information": COLOR_INFO,
    "Warning": COLOR_WARNING,
    "High": "#f97316",
    "Critical": COLOR_CRITICAL,
}
