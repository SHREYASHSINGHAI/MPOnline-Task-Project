# =============================================================
#  models.py  --  Database Helper Functions  (SQLite)
#  Uses Python's built-in sqlite3 — no installation needed!
# =============================================================

import sqlite3
from config import DB_PATH


# ── Connection ────────────────────────────────────────────────

def get_connection():
    """Return a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    return conn


# ── Init DB (called once on first run) ────────────────────────

def init_db():
    """Create the tasks table and seed sample data if empty."""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT    NOT NULL,
            task_title    TEXT    NOT NULL,
            completed     INTEGER DEFAULT 0,
            created_at    TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # Seed only if table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        sample = [
            ('Alice Johnson',   'Design UI Mockups',        1),
            ('Bob Smith',       'Set Up Database Schema',   1),
            ('Carol Williams',  'Implement REST API',       0),
            ('David Lee',       'Write Unit Tests',         0),
            ('Eve Martinez',    'Deploy to Staging Server', 0),
            ('Frank Brown',     'Code Review and QA',       0),
            ('Grace Chen',      'Client Presentation Prep', 1),
            ('Henry Wilson',    'Documentation Update',     0),
        ]
        cursor.executemany(
            "INSERT INTO tasks (employee_name, task_title, completed) VALUES (?, ?, ?)",
            sample
        )

    conn.commit()
    conn.close()


# ── READ ──────────────────────────────────────────────────────

def get_all_tasks(search=None, completed=None):
    """Fetch all tasks with optional filters."""
    conn   = get_connection()
    cursor = conn.cursor()

    query  = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if search:
        query += " AND (employee_name LIKE ? OR task_title LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]

    if completed is not None:
        query += " AND completed = ?"
        params.append(1 if completed else 0)

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_task(task_id):
    """Fetch a single task by primary key."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ── CREATE ────────────────────────────────────────────────────

def create_task(employee_name, task_title, completed=False):
    """Insert a new task and return its ID."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (employee_name, task_title, completed) VALUES (?, ?, ?)",
        (employee_name, task_title, 1 if completed else 0),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


# ── UPDATE ────────────────────────────────────────────────────

def update_task(task_id, employee_name=None, task_title=None, completed=None):
    """Update one or more fields of an existing task."""
    fields, params = [], []

    if employee_name is not None:
        fields.append("employee_name = ?")
        params.append(employee_name)
    if task_title is not None:
        fields.append("task_title = ?")
        params.append(task_title)
    if completed is not None:
        fields.append("completed = ?")
        params.append(1 if completed else 0)

    if not fields:
        return 0

    conn   = get_connection()
    cursor = conn.cursor()
    params.append(task_id)
    cursor.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE task_id = ?", params)
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected


# ── DELETE ────────────────────────────────────────────────────

def delete_task(task_id):
    """Delete a task by primary key."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected


# ── STATS ─────────────────────────────────────────────────────

def get_stats():
    """Return aggregate statistics for the dashboard."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*)                      AS total,
            SUM(CASE WHEN completed=1 THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN completed=0 THEN 1 ELSE 0 END) AS pending,
            COUNT(DISTINCT employee_name)                 AS employees
        FROM tasks
    """)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}
