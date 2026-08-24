"""
auth.py — Student authentication (self-service signup + login).

Passwords are never stored in plaintext: each password is hashed with
PBKDF2-HMAC-SHA256 (100,000 iterations) and a unique random salt per
student, using only Python's standard library (no extra dependency).

This is intentionally separate from the Admin/Agent login (which continues
to use its existing fixed-credential-dict pattern in app.py) — students get
real, self-service accounts backed by the database.
"""

import hashlib
import re
import secrets

import database as db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _hash_password(password: str, salt: str = None):
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
    ).hex()
    return pwd_hash, salt


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip()))


def signup_student(email: str, password: str, name: str, roll_no: str):
    """Returns (success: bool, message: str)."""
    email = (email or "").strip().lower()
    password = password or ""
    name = (name or "").strip()

    if not email or not password or not name:
        return False, "Please fill in your name, email, and password."
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if db.get_student_by_email(email):
        return False, "An account with this email already exists. Please log in instead."

    pwd_hash, salt = _hash_password(password)
    db.insert_student(email, pwd_hash, salt, name, roll_no)
    return True, "Account created successfully! You can now log in."


def login_student(email: str, password: str):
    """Returns the student record dict on success, or None on failure."""
    email = (email or "").strip().lower()
    if not email or not password:
        return None
    record = db.get_student_by_email(email)
    if not record:
        return None
    pwd_hash, _ = _hash_password(password, record["salt"])
    if secrets.compare_digest(pwd_hash, record["password_hash"]):
        return record
    return None
