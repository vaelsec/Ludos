import re
import sqlite3
import unittest
from pathlib import Path

SCHEMA = Path(__file__).resolve().parent.parent / "schema"


def columns(sql):
    """{table: [column names]} from CREATE TABLE blocks (both dialects)."""
    out = {}
    for m in re.finditer(r"CREATE TABLE IF NOT EXISTS (\w+) \((.*?)\n\)", sql, re.S):
        cols = []
        for line in m.group(2).splitlines():
            line = line.split("--")[0].strip()
            if line and not line.upper().startswith(("KEY", "PRIMARY", "UNIQUE")):
                cols.append(line.split()[0])
        out[m.group(1)] = cols
    return out


def db():
    conn = sqlite3.connect(":memory:")
    conn.executescript((SCHEMA / "schema.sqlite.sql").read_text())
    return conn


def add_activity(conn, i, when, typ):
    conn.execute("INSERT INTO activity (id, start_time, type) VALUES (?,?,?)", (i, when, typ))


def add_entry(conn, day, strength):
    conn.execute("INSERT INTO daily_entry (entry_date, strength_done) VALUES (?,?)", (day, strength))


class SchemaTests(unittest.TestCase):
    def test_dialects_define_same_tables_and_columns(self):
        lite = columns((SCHEMA / "schema.sqlite.sql").read_text())
        maria = columns((SCHEMA / "schema.mariadb.sql").read_text())
        self.assertEqual(set(lite), {"activity", "daily_entry"})
        self.assertEqual(lite, maria)

    def test_form_fields_present(self):
        cols = columns((SCHEMA / "schema.sqlite.sql").read_text())["daily_entry"]
        for f in ("knee_l", "knee_r", "quad_tightness", "strength_done", "mobility_done",
                  "energy", "mood", "weight_kg", "gut_status", "notes"):
            self.assertIn(f, cols)

    def test_strength_day_counts_a_day_once_and_keeps_both_flags(self):
        c = db()
        add_activity(c, 1, "2026-10-05 18:00:00", "strength_training")
        add_entry(c, "2026-10-05", 1)       # both sources agree
        add_activity(c, 2, "2026-10-08 18:30:00", "strength_training")  # garmin only
        add_entry(c, "2026-10-10", 1)       # form only
        add_activity(c, 3, "2026-10-06 07:00:00", "running")            # not strength
        add_entry(c, "2026-10-07", 0)       # unticked
        rows = {r[0]: r[1:] for r in c.execute("SELECT day, garmin_strength, form_strength FROM strength_day")}
        self.assertEqual(rows, {"2026-10-05": (1, 1), "2026-10-08": (1, 0), "2026-10-10": (0, 1)})

    def test_two_garmin_sessions_same_day_count_once(self):
        c = db()
        add_activity(c, 1, "2026-10-05 07:00:00", "strength_training")
        add_activity(c, 2, "2026-10-05 19:00:00", "strength_training")
        self.assertEqual(c.execute("SELECT COUNT(*) FROM strength_day").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
