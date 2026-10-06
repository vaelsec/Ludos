"""Backfill from the Garmin account export (Data Management > Export Your Data).

UNVERIFIED against a real export: field names and units below follow the commonly seen
DI-Connect-Fitness *_summarizedActivities.json layout. Confirm with a sample before trusting
the 9-year backfill (the CLI prints a few converted rows for inspection).
"""
import json
from datetime import datetime
from pathlib import Path

from .db import connect, upsert

# Assumed export units: distance in cm, duration in ms, elevation in cm, times as epoch ms.
DIST_TO_M = 0.01
DUR_TO_S = 0.001
ELEV_TO_M = 0.01


def _num(v, f=1.0):
    return None if v is None else v * f


def map_export_activity(a):
    start = datetime.fromtimestamp(a["startTimeLocal"] / 1000)  # export stores local wall time as epoch ms
    return {
        "id": int(a["activityId"]),
        "start_time": start.strftime("%Y-%m-%d %H:%M:%S"),
        "type": a.get("activityType", "other"),
        "name": a.get("name"),
        "distance_m": _num(a.get("distance"), DIST_TO_M),
        "duration_s": _num(a.get("duration"), DUR_TO_S),
        "elevation_gain_m": _num(a.get("elevationGain"), ELEV_TO_M),
        "avg_hr": a.get("avgHr"),
        "max_hr": a.get("maxHr"),
        "avg_power": a.get("avgPower"),
        "calories": a.get("calories"),
        "training_effect": a.get("aerobicTrainingEffect"),
        "source": "garmin_export",
    }


def import_export(root, conn=None):
    conn = conn or connect()
    n = 0
    for f in Path(root).rglob("*summarizedActivities*.json"):
        data = json.loads(f.read_text())
        for block in data:
            for a in block.get("summarizedActivitiesExport", []):
                upsert(conn, "activities", map_export_activity(a), "id")
                n += 1
    conn.commit()
    return n
