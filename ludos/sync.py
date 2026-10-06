"""Daily sync via the unofficial garminconnect library (credentials in .env or environment)."""
import os
from datetime import date, timedelta
from pathlib import Path

from .db import connect, upsert

TOKENS = Path(os.environ.get("LUDOS_TOKENS", Path(__file__).resolve().parent.parent / ".garmin_tokens"))


def _client():
    from garminconnect import Garmin
    api = Garmin(os.environ["GARMIN_EMAIL"], os.environ["GARMIN_PASSWORD"])
    api.login(str(TOKENS))  # reuses cached tokens; stores them after first login
    return api


def map_activity(a):
    return {
        "id": a["activityId"],
        "start_time": a["startTimeLocal"],
        "type": (a.get("activityType") or {}).get("typeKey", "other"),
        "name": a.get("activityName"),
        "distance_m": a.get("distance"),
        "duration_s": a.get("duration"),
        "elevation_gain_m": a.get("elevationGain"),
        "avg_hr": a.get("averageHR"),
        "max_hr": a.get("maxHR"),
        "avg_power": a.get("avgPower"),
        "calories": a.get("calories"),
        "training_effect": a.get("aerobicTrainingEffect"),
        "source": "garmin_api",
    }


def map_daily(day, stats, sleep, hrv):
    ds = (sleep or {}).get("dailySleepDTO") or {}
    scores = (ds.get("sleepScores") or {}).get("overall") or {}
    hv = ((hrv or {}).get("hrvSummary") or {})
    return {
        "date": day,
        "steps": stats.get("totalSteps"),
        "resting_hr": stats.get("restingHeartRate"),
        "sleep_s": ds.get("sleepTimeSeconds"),
        "sleep_score": scores.get("value"),
        "hrv_ms": hv.get("lastNightAvg"),
        "body_battery_max": stats.get("bodyBatteryHighestValue"),
        "body_battery_min": stats.get("bodyBatteryLowestValue"),
        "stress_avg": stats.get("averageStressLevel"),
    }


def map_weights(comp):
    for w in (comp or {}).get("dateWeightList") or []:
        grams = w.get("weight")
        if not grams:
            continue
        yield {
            "date": w["calendarDate"],
            "weight_kg": round(grams / 1000, 2),
            "body_fat_pct": w.get("bodyFat"),
            "muscle_kg": round(w["muscleMass"] / 1000, 2) if w.get("muscleMass") else None,
            "bmi": w.get("bmi"),
        }


def sync(days=7, conn=None):
    api = _client()
    conn = conn or connect()
    end = date.today()
    start = end - timedelta(days=days)
    for a in api.get_activities_by_date(start.isoformat(), end.isoformat()):
        upsert(conn, "activities", map_activity(a), "id")
    for w in map_weights(api.get_body_composition(start.isoformat(), end.isoformat())):
        upsert(conn, "weight", w, "date")
    for i in range(days + 1):
        day = (start + timedelta(days=i)).isoformat()
        try:
            upsert(conn, "daily", map_daily(day, api.get_stats(day), api.get_sleep_data(day), api.get_hrv_data(day)), "date")
        except Exception as e:  # one missing day should not abort the sync
            print(f"{day}: skipped ({e})")
    conn.commit()
