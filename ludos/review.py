"""Builds the prompt packet for the daily narrative review (written by Claude, stored in `reviews`)."""
from datetime import date, timedelta
from pathlib import Path

from .db import RUN_TYPES, upsert
from .stats import overview, rollup, weight_series

ROOT = Path(__file__).resolve().parent.parent
CONTEXT_FILE = ROOT / "context" / "context.md"


def build_packet(conn, today=None):
    today = today or date.today()
    ctx = CONTEXT_FILE.read_text() if CONTEXT_FILE.exists() else "(no context/context.md yet)"
    since = (today - timedelta(days=14)).isoformat()
    runs = conn.execute(
        f"SELECT start_time, type, ROUND(distance_m/1000.0,2) km, ROUND(duration_s/60.0,1) min, "
        f"elevation_gain_m elev, avg_hr, avg_power FROM activities WHERE date(start_time) >= ? "
        f"ORDER BY start_time", (since,)).fetchall()
    daily = conn.execute("SELECT * FROM daily WHERE date >= ? ORDER BY date", (since,)).fetchall()
    lines = [f"# Daily review packet, {today}", "", "## Athlete context", ctx, "",
             "## Overview", str(overview(conn, today)), "", "## Last 14 days: activities"]
    lines += [", ".join(f"{k}={r[k]}" for k in r.keys()) for r in runs]
    lines += ["", "## Last 14 days: daily wellness"]
    lines += [", ".join(f"{k}={r[k]}" for k in r.keys()) for r in daily]
    lines += ["", "## Last 12 weeks: weekly running"]
    lines += [str(r) for r in rollup(conn, "week", since=(today - timedelta(weeks=12)).isoformat())]
    lines += ["", "## Weight (last 8 weeks, 7-day average)"]
    lines += [f"{w['date']}: {w['avg7']} kg" for w in weight_series(conn, (today - timedelta(weeks=8)).isoformat())[::3]]
    lines += ["", "## Task", "Write a short narrative review of yesterday and the trend, then 2-3 concrete "
              "recommendations for today. Be direct and quantitative; flag injury or overload risk."]
    return "\n".join(lines)


def save_review(conn, text, day=None):
    upsert(conn, "reviews", {"date": str(day or date.today()), "text": text}, "date")
    conn.commit()
