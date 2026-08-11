"""Authentication and authorization helpers for FacilityOps AI.

Uses PBKDF2-HMAC-SHA256 password hashing and a local JSON credential store.
This is suitable for a local/demo Streamlit deployment. For production,
replace the local store with a managed identity provider or database-backed
service and serve the app only over HTTPS.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_STORE = BASE_DIR / "data" / "auth_users.json"
PBKDF2_ITERATIONS = 310_000
DEFAULT_FAILED_LOGIN_LIMIT = 5
LOCKOUT_SECONDS = 60

# Demo bootstrap accounts. Passwords are hashed before being persisted.
# Override these with environment variables before first run if desired.
BOOTSTRAP_USERS = {
    "admin": {
        "password_env": "FACILITYOPS_ADMIN_PASSWORD",
        "default_password": "admin123",
        "full_name": "Admin Administrator",
        "email": "admin@facilityops.com",
        "role": "Administrator",
    },
    "manager": {
        "password_env": "FACILITYOPS_MANAGER_PASSWORD",
        "default_password": "manager123",
        "full_name": "Facility Manager",
        "email": "manager@facilityops.com",
        "role": "Facility Manager",
    },
}

ROLE_PAGE_ACCESS = {
    "Administrator": None,  # None means all pages.
    "Facility Manager": {
        "Overview", "Dashboard", "AI Agents", "Modules", "Work Orders", "Assets",
        "Monitoring", "Analytics", "Reports", "Alerts", "Integrations", "Settings",
    },
    "Maintenance Manager": {
        "Overview", "Dashboard", "AI Agents", "Work Orders", "Assets", "Monitoring",
        "Analytics", "Reports", "Alerts",
    },
    "Technician": {"Overview", "Work Orders", "Assets", "Monitoring", "Alerts"},
    "Security Officer": {"Overview", "Monitoring", "Reports", "Alerts"},
    "Analyst": {"Overview", "Dashboard", "Analytics", "Reports"},
    "Viewer": {"Overview", "Dashboard", "Monitoring", "Analytics", "Reports"},
}


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected = base64.b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, int(iterations)
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _bootstrap_store() -> dict:
    AUTH_STORE.parent.mkdir(parents=True, exist_ok=True)
    users = {}
    for username, info in BOOTSTRAP_USERS.items():
        password = os.environ.get(info["password_env"], info["default_password"])
        users[username] = {
            "username": username,
            "email": info["email"],
            "full_name": info["full_name"],
            "role": info["role"],
            "status": "Active",
            "password_hash": _hash_password(password),
            "last_login": "",
        }
    payload = {"version": 1, "users": users}
    _save_store(payload)
    return payload


def _load_store() -> dict:
    if not AUTH_STORE.exists():
        return _bootstrap_store()
    try:
        with AUTH_STORE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data.get("users"), dict):
            raise ValueError("Invalid auth store")
        return data
    except (OSError, json.JSONDecodeError, ValueError):
        # Do not silently overwrite a damaged credential file.
        return {"version": 1, "users": {}}


def _save_store(payload: dict) -> None:
    AUTH_STORE.parent.mkdir(parents=True, exist_ok=True)
    temp_path = AUTH_STORE.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    os.replace(temp_path, AUTH_STORE)


def init_session_state() -> None:
    defaults = {
        "auth_logged_in": False,
        "auth_username": "",
        "auth_full_name": "",
        "auth_role": "",
        "auth_login_time": 0.0,
        "auth_last_activity": 0.0,
        "current_page": "Overview",
        "login_error": "",
        "failed_login_attempts": 0,
        "auth_locked_until": 0.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _find_user(identifier: str) -> dict | None:
    identifier = (identifier or "").strip().lower()
    if not identifier:
        return None
    for user in _load_store().get("users", {}).values():
        if identifier in {
            str(user.get("username", "")).lower(),
            str(user.get("email", "")).lower(),
        }:
            return user
    return None


def attempt_login(identifier: str, password: str) -> bool:
    now = time.time()
    locked_until = float(st.session_state.get("auth_locked_until", 0.0) or 0.0)
    if now < locked_until:
        remaining = max(1, int(locked_until - now))
        st.session_state.login_error = f"Too many failed attempts. Try again in {remaining} seconds."
        return False

    user = _find_user(identifier)
    valid = bool(
        user
        and user.get("status", "Active") == "Active"
        and _verify_password(password or "", user.get("password_hash", ""))
    )

    if valid:
        st.session_state.auth_logged_in = True
        st.session_state.auth_username = user["username"]
        st.session_state.auth_full_name = user.get("full_name", user["username"])
        st.session_state.auth_role = user.get("role", "Viewer")
        st.session_state.auth_login_time = now
        st.session_state.auth_last_activity = now
        st.session_state.login_error = ""
        st.session_state.failed_login_attempts = 0
        st.session_state.auth_locked_until = 0.0
        _record_last_login(user["username"])
        return True

    attempts = int(st.session_state.get("failed_login_attempts", 0)) + 1
    st.session_state.failed_login_attempts = attempts
    if attempts >= DEFAULT_FAILED_LOGIN_LIMIT:
        st.session_state.auth_locked_until = now + LOCKOUT_SECONDS
        st.session_state.failed_login_attempts = 0
        st.session_state.login_error = "Too many failed attempts. Login is temporarily locked for 60 seconds."
    else:
        st.session_state.login_error = "Invalid username/email or password."
    return False


def _record_last_login(username: str) -> None:
    payload = _load_store()
    user = payload.get("users", {}).get(username)
    if not user:
        return
    user["last_login"] = datetime.now().isoformat(timespec="seconds")
    try:
        _save_store(payload)
    except OSError:
        pass


def logout() -> None:
    for key, value in {
        "auth_logged_in": False,
        "auth_username": "",
        "auth_full_name": "",
        "auth_role": "",
        "auth_login_time": 0.0,
        "auth_last_activity": 0.0,
        "current_page": "Overview",
        "login_error": "",
    }.items():
        st.session_state[key] = value


def is_logged_in() -> bool:
    return bool(st.session_state.get("auth_logged_in", False))


def current_user_label() -> str:
    return st.session_state.get("auth_full_name") or st.session_state.get("auth_username", "Guest")


def current_role() -> str:
    return st.session_state.get("auth_role", "Viewer")


def can_access_page(page_name: str) -> bool:
    role = current_role()
    allowed = ROLE_PAGE_ACCESS.get(role, {"Overview"})
    return True if allowed is None else page_name in allowed


def allowed_pages(page_names: list[str]) -> list[str]:
    return [name for name in page_names if can_access_page(name)]


def change_password(username: str, current_password: str, new_password: str) -> tuple[bool, str]:
    if len(new_password or "") < 8:
        return False, "New password must be at least 8 characters long."
    payload = _load_store()
    user = payload.get("users", {}).get((username or "").lower())
    if not user or not _verify_password(current_password or "", user.get("password_hash", "")):
        return False, "Current password is incorrect."
    user["password_hash"] = _hash_password(new_password)
    _save_store(payload)
    return True, "Password changed successfully."
