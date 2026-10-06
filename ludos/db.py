import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("LUDOS_DB", Path(__file__).resolve().parent.parent / "data" / "ludos.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY,
    start_time TEXT NOT NULL,          -- local time, ISO 'YYYY-MM-DD HH:MM:SS'
    type TEXT NOT NULL,
    name TEXT,
    distance_m REAL,
    duration_s REAL,
    elevation_gain_m REAL,
    avg_hr REAL,
    max_hr REAL,
    avg_power REAL,
    calories REAL,
    training_effect REAL,
    source TEXT
);
CREATE INDEX IF NOT EXISTS idx_activities_start ON activities(start_time);

CREATE TABLE IF NOT EXISTS daily (
    date TEXT PRIMARY KEY,
    steps INTEGER,
    resting_hr INTEGER,
    sleep_s INTEGER,
    sleep_score INTEGER,
    hrv_ms REAL,
    body_battery_max INTEGER,
    body_battery_min INTEGER,
    stress_avg INTEGER
);

CREATE TABLE IF NOT EXISTS weight (
    date TEXT PRIMARY KEY,
    weight_kg REAL,
    body_fat_pct REAL,
    muscle_kg REAL,
    bmi REAL
);

CREATE TABLE IF NOT EXISTS reviews (
    date TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

RUN_TYPES = ("running", "trail_running", "treadmill_running", "track_running", "virtual_run")


def connect(path=None):
    p = Path(path or DB_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def upsert(conn, table, row, key):
    cols = list(row)
    placeholders = ",".join("?" for _ in cols)
    updates = ",".join(f"{c}=excluded.{c}" for c in cols if c != key)
    conn.execute(
        f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders}) "
        f"ON CONFLICT({key}) DO UPDATE SET {updates}",
        [row[c] for c in cols],
    )
