"""Synthetic demo data so the dashboard can be developed without personal data."""
import random
from datetime import date, timedelta

from .db import connect, upsert


def seed(conn=None, days=400, today=None):
    rnd = random.Random(42)
    conn = conn or connect()
    today = today or date.today()
    for i in range(days, -1, -1):
        d = today - timedelta(days=i)
        ramp = 1 + (days - i) / days  # volume builds over time
        if rnd.random() < 0.7:
            km = round(rnd.uniform(5, 10) * ramp * (1.6 if d.weekday() == 6 else 1), 2)
            pace = rnd.uniform(5.6, 6.6)
            upsert(conn, "activities", {
                "id": int(d.strftime("%Y%m%d")) * 10, "start_time": f"{d} 07:30:00",
                "type": rnd.choice(["running", "running", "trail_running"]), "name": "Demo run",
                "distance_m": km * 1000, "duration_s": km * pace * 60,
                "elevation_gain_m": km * rnd.uniform(5, 40), "avg_hr": rnd.randint(140, 160),
                "max_hr": rnd.randint(165, 180), "avg_power": rnd.randint(200, 260),
                "calories": km * 70, "training_effect": round(rnd.uniform(2, 4), 1), "source": "seed"}, "id")
        upsert(conn, "daily", {
            "date": str(d), "steps": rnd.randint(5000, 14000), "resting_hr": rnd.randint(50, 58),
            "sleep_s": rnd.randint(5 * 3600, 8 * 3600), "sleep_score": rnd.randint(60, 90),
            "hrv_ms": rnd.randint(45, 80), "body_battery_max": rnd.randint(70, 100),
            "body_battery_min": rnd.randint(5, 30), "stress_avg": rnd.randint(20, 45)}, "date")
        if i % 2 == 0:
            upsert(conn, "weight", {
                "date": str(d), "weight_kg": round(92 - (days - i) / days * 8 + rnd.uniform(-0.6, 0.6), 1),
                "body_fat_pct": round(26 - (days - i) / days * 4 + rnd.uniform(-.3, .3), 1),
                "muscle_kg": round(38 + rnd.uniform(-.3, .3), 1), "bmi": None}, "date")
    conn.commit()
