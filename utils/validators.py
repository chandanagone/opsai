"""Simple, dependency-free validators used by forms across the app."""

import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[+0-9\-\s()]{7,20}$")


def is_valid_email(email: str) -> bool:
    return bool(email) and bool(EMAIL_RE.match(email.strip()))


def is_valid_phone(phone: str) -> bool:
    return bool(phone) and bool(PHONE_RE.match(phone.strip()))


def is_non_empty(value) -> bool:
    return value is not None and str(value).strip() != ""


def is_positive_number(value) -> bool:
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def is_valid_date_range(start, end) -> bool:
    if start is None or end is None:
        return False
    return start <= end


def duplicate_email_exists(df, email: str, id_column: str = None, exclude_id=None) -> bool:
    if df is None or df.empty or "Email" not in df.columns:
        return False
    mask = df["Email"].str.lower() == email.strip().lower()
    if exclude_id and id_column:
        mask &= df[id_column] != exclude_id
    return bool(mask.any())


def validation_errors(rules: dict) -> list:
    """rules: {field_name: (is_valid_bool, error_message)}"""
    errors = []
    for field, (valid, message) in rules.items():
        if not valid:
            errors.append(message)
    return errors
