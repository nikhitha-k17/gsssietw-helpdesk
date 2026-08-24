"""
database.py — SQLite persistence layer for the College Help Desk.

Why this exists: the original app kept everything in Streamlit's
st.session_state, which is private to a single browser session — that's why
Lost & Found posts, tickets, applications, etc. never showed up for anyone
else. This module gives every part of the app a single shared, durable store.

Retention policy: every row that represents "student search/submission
information" carries a created_at timestamp. Records older than
RETENTION_DAYS are:
  1. Excluded from every SELECT query (defense in depth — expired rows never
     render anywhere, even if cleanup hasn't run yet), AND
  2. Physically DELETEd by a background cleanup thread (see
     start_cleanup_scheduler) that runs periodically for as long as the app
     process is alive, plus once synchronously at startup.

Streamlit has no built-in cron/job runner, so a daemon thread inside the same
process is the safest practical mechanism available in this architecture.
"""

import hashlib
import json
import os
import secrets
import sqlite3
import threading
import time
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "helpdesk.db")
RETENTION_DAYS = 30

_write_lock = threading.Lock()  # sqlite + multiple threads (cleanup + Streamlit)


# ----------------------------------------------------------------------------
# Connection & schema
# ----------------------------------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    with _write_lock:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                name TEXT,
                roll_no TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS search_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_email TEXT,
                query TEXT,
                category TEXT,
                matched INTEGER,
                source TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE,
                student_email TEXT,
                name TEXT, roll_no TEXT, email TEXT, phone TEXT,
                category TEXT, priority TEXT, description TEXT,
                status TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS lost_found (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT UNIQUE,
                student_email TEXT,
                type TEXT, item_name TEXT, category TEXT, location TEXT,
                event_date TEXT, description TEXT, reporter_name TEXT, contact TEXT,
                photo BLOB,
                status TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id TEXT UNIQUE,
                student_email TEXT,
                type TEXT, name TEXT, roll_no TEXT, program TEXT, email TEXT, phone TEXT,
                extra_json TEXT, remarks TEXT, status TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS canteen_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_email TEXT,
                date TEXT, meal TEXT, rating INTEGER, comments TEXT, name TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_search_created ON search_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at);
            CREATE INDEX IF NOT EXISTS idx_lf_created ON lost_found(created_at);
            CREATE INDEX IF NOT EXISTS idx_apps_created ON applications(created_at);
            CREATE INDEX IF NOT EXISTS idx_feedback_created ON canteen_feedback(created_at);
            """
        )
        conn.commit()
    conn.close()


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _cutoff():
    return (datetime.now() - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------------------------------------------------------
# 30-day retention: cleanup
# ----------------------------------------------------------------------------
RETAINED_TABLES = ["search_logs", "tickets", "lost_found", "applications", "canteen_feedback"]


def cleanup_expired_records():
    """Physically DELETE rows older than RETENTION_DAYS from every retained table.
    Safe to call repeatedly/concurrently."""
    conn = get_connection()
    cutoff = _cutoff()
    with _write_lock:
        for table in RETAINED_TABLES:
            conn.execute(f"DELETE FROM {table} WHERE created_at < ?", (cutoff,))
        conn.commit()
    conn.close()


_scheduler_started = False
_scheduler_lock = threading.Lock()


def start_cleanup_scheduler(interval_seconds=3600):
    """Start a background daemon thread that deletes expired records on a
    recurring schedule. Idempotent — safe to call on every Streamlit rerun;
    only the first call actually starts the thread."""
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        _scheduler_started = True

    def _loop():
        while True:
            try:
                cleanup_expired_records()
            except Exception:
                pass
            time.sleep(interval_seconds)

    t = threading.Thread(target=_loop, daemon=True, name="helpdesk-retention-cleanup")
    t.start()


# ----------------------------------------------------------------------------
# Students
# ----------------------------------------------------------------------------
def get_student_by_email(email):
    conn = get_connection()
    row = conn.execute("SELECT * FROM students WHERE email = ?", (email.strip().lower(),)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_student(email, password_hash, salt, name, roll_no):
    conn = get_connection()
    with _write_lock:
        conn.execute(
            "INSERT INTO students (email, password_hash, salt, name, roll_no, created_at) VALUES (?,?,?,?,?,?)",
            (email.strip().lower(), password_hash, salt, name, roll_no, _now()),
        )
        conn.commit()
    conn.close()


# ----------------------------------------------------------------------------
# Search logs (student search/submission activity)
# ----------------------------------------------------------------------------
def insert_search_log(query, category, matched, source="Chat", student_email=None):
    conn = get_connection()
    with _write_lock:
        conn.execute(
            "INSERT INTO search_logs (student_email, query, category, matched, source, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (student_email, query, category or "Unmatched", int(bool(matched)), source, _now()),
        )
        conn.commit()
    conn.close()


def get_search_logs(limit=500):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM search_logs WHERE created_at >= ? ORDER BY created_at DESC LIMIT ?",
        (_cutoff(), limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ----------------------------------------------------------------------------
# Tickets
# ----------------------------------------------------------------------------
def insert_ticket(ticket_id, student_email, name, roll_no, email, phone, category, priority, description):
    conn = get_connection()
    with _write_lock:
        conn.execute(
            "INSERT INTO tickets (ticket_id, student_email, name, roll_no, email, phone, category, "
            "priority, description, status, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (ticket_id, student_email, name, roll_no, email, phone, category, priority, description,
             "Open", _now()),
        )
        conn.commit()
    conn.close()


def get_tickets(student_email=None, limit=500):
    conn = get_connection()
    if student_email:
        rows = conn.execute(
            "SELECT * FROM tickets WHERE created_at >= ? AND student_email = ? ORDER BY created_at DESC LIMIT ?",
            (_cutoff(), student_email, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM tickets WHERE created_at >= ? ORDER BY created_at DESC LIMIT ?",
            (_cutoff(), limit),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_ticket_status(ticket_id, new_status):
    conn = get_connection()
    with _write_lock:
        conn.execute("UPDATE tickets SET status = ? WHERE ticket_id = ?", (new_status, ticket_id))
        conn.commit()
    conn.close()


# ----------------------------------------------------------------------------
# Lost & Found
# ----------------------------------------------------------------------------
def insert_lost_found(report_id, student_email, item_type, item_name, category, location,
                       event_date, description, reporter_name, contact, photo_bytes):
    conn = get_connection()
    with _write_lock:
        conn.execute(
            "INSERT INTO lost_found (report_id, student_email, type, item_name, category, location, "
            "event_date, description, reporter_name, contact, photo, status, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (report_id, student_email, item_type, item_name, category, location, event_date,
             description, reporter_name, contact, photo_bytes, "Open", _now()),
        )
        conn.commit()
    conn.close()


def get_all_lost_found(limit=500):
    """Global, shared notice board — every student sees every report."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM lost_found WHERE created_at >= ? ORDER BY created_at DESC LIMIT ?",
        (_cutoff(), limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_lost_found_status(report_id, new_status):
    conn = get_connection()
    with _write_lock:
        conn.execute("UPDATE lost_found SET status = ? WHERE report_id = ?", (new_status, report_id))
        conn.commit()
    conn.close()


# ----------------------------------------------------------------------------
# Applications
# ----------------------------------------------------------------------------
def insert_application(app_id, student_email, app_type, name, roll_no, program, email, phone,
                        extra_fields, remarks):
    conn = get_connection()
    with _write_lock:
        conn.execute(
            "INSERT INTO applications (app_id, student_email, type, name, roll_no, program, email, "
            "phone, extra_json, remarks, status, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (app_id, student_email, app_type, name, roll_no, program, email, phone,
             json.dumps(extra_fields), remarks, "Submitted", _now()),
        )
        conn.commit()
    conn.close()


def get_applications(student_email=None, limit=500):
    conn = get_connection()
    if student_email:
        rows = conn.execute(
            "SELECT * FROM applications WHERE created_at >= ? AND student_email = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (_cutoff(), student_email, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM applications WHERE created_at >= ? ORDER BY created_at DESC LIMIT ?",
            (_cutoff(), limit),
        ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["extra"] = json.loads(d.pop("extra_json") or "{}")
        result.append(d)
    return result


def update_application_status(app_id, new_status):
    conn = get_connection()
    with _write_lock:
        conn.execute("UPDATE applications SET status = ? WHERE app_id = ?", (new_status, app_id))
        conn.commit()
    conn.close()


# ----------------------------------------------------------------------------
# Canteen feedback
# ----------------------------------------------------------------------------
def insert_feedback(student_email, date, meal, rating, comments, name):
    conn = get_connection()
    with _write_lock:
        conn.execute(
            "INSERT INTO canteen_feedback (student_email, date, meal, rating, comments, name, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (student_email, date, meal, rating, comments, name, _now()),
        )
        conn.commit()
    conn.close()


def get_all_feedback(limit=500):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM canteen_feedback WHERE created_at >= ? ORDER BY created_at DESC LIMIT ?",
        (_cutoff(), limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ----------------------------------------------------------------------------
# 30-day summary (used by Admin & Agent dashboards)
# ----------------------------------------------------------------------------
def get_summary_counts():
    conn = get_connection()
    cutoff = _cutoff()
    counts = {}
    for table in RETAINED_TABLES:
        counts[table] = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE created_at >= ?", (cutoff,)
        ).fetchone()[0]
    conn.close()
    return counts


def get_category_counts():
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, COUNT(*) c FROM search_logs WHERE created_at >= ? GROUP BY category ORDER BY c DESC",
        (_cutoff(),),
    ).fetchall()
    conn.close()
    return {r["category"]: r["c"] for r in rows}


def get_status_counts(table, status_column="status"):
    conn = get_connection()
    rows = conn.execute(
        f"SELECT {status_column}, COUNT(*) c FROM {table} WHERE created_at >= ? GROUP BY {status_column}",
        (_cutoff(),),
    ).fetchall()
    conn.close()
    return {r[status_column]: r["c"] for r in rows}
