from datetime import date, timedelta

from .db import RUN_TYPES

_RUN = ",".join("?" for _ in RUN_TYPES)
_PERIOD_SQL = {
    "day": "date(start_time)",
    "week": "date(start_time, '-6 days', 'weekday 1')",  # Monday of the ISO week
    "month": "strftime('%Y-%m-01', start_time)",
}


def rollup(conn, period="week", since=None):
    if period not in _PERIOD_SQL:
        raise ValueError(period)
    key = _PERIOD_SQL[period]
    params = list(RUN_TYPES)
    where = f"type IN ({_RUN})"
    if since:
        where += " AND date(start_time) >= ?"
        params.append(since)
    rows = conn.execute(
        f"""SELECT {key} AS period,
                   COUNT(*) AS runs,
                   ROUND(SUM(distance_m)/1000.0, 2) AS km,
                   ROUND(SUM(duration_s)/3600.0, 2) AS hours,
                   ROUND(SUM(elevation_gain_m), 0) AS elevation_m,
                   ROUND(MAX(distance_m)/1000.0, 2) AS longest_km,
                   ROUND(AVG(avg_hr), 0) AS avg_hr,
                   ROUND(SUM(duration_s)/60.0 / NULLIF(SUM(distance_m)/1000.0, 0), 2) AS pace_min_km
            FROM activities WHERE {where}
            GROUP BY period ORDER BY period""",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def weight_series(conn, since=None):
    rows = [dict(r) for r in conn.execute(
        "SELECT date, weight_kg, body_fat_pct, muscle_kg FROM weight "
        "WHERE weight_kg IS NOT NULL ORDER BY date").fetchall()]
    for i, r in enumerate(rows):
        window = [x["weight_kg"] for x in rows[max(0, i - 6):i + 1]]
        r["avg7"] = round(sum(window) / len(window), 2)
    if since:
        rows = [r for r in rows if r["date"] >= since]
    return rows


def overview(conn, today=None):
    today = today or date.today()
    def km_between(start, end):  # [start, end) in days before today
        lo, hi = (today - timedelta(days=start)).isoformat(), (today - timedelta(days=end)).isoformat()
        q = ",".join("?" for _ in RUN_TYPES)
        r = conn.execute(f"SELECT COALESCE(SUM(distance_m),0)/1000.0 FROM activities WHERE type IN ({q}) "
                         "AND date(start_time) > ? AND date(start_time) <= ?", [*RUN_TYPES, lo, hi]).fetchone()
        return r[0]

    # trailing 7 days vs the average of the preceding 4 x 7 days (avoids partial-week distortion)
    this_week = round(km_between(7, 0), 1)
    base = km_between(35, 7) / 4
    ramp = round((this_week - base) / base * 100, 1) if base else None
    w = weight_series(conn)
    latest = w[-1] if w else None
    month_ago = next((x for x in reversed(w) if x["date"] <= (today - timedelta(days=28)).isoformat()), None)
    d = conn.execute("SELECT * FROM daily ORDER BY date DESC LIMIT 1").fetchone()
    return {
        "week_km": this_week,
        "prev4_avg_km": round(base, 1),
        "ramp_pct": ramp,
        "weight_kg": latest["avg7"] if latest else None,
        "weight_change_4w": round(latest["avg7"] - month_ago["avg7"], 2) if latest and month_ago else None,
        "latest_daily": dict(d) if d else None,
    }
