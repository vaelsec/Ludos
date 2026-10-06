from datetime import date

from ludos import stats
from ludos.db import connect, upsert
from ludos.importer import map_export_activity
from ludos.review import build_packet
from ludos.seed import seed
from ludos.sync import map_activity, map_weights


def mem():
    return connect(":memory:")


def run(conn, i, day, km, typ="running"):
    upsert(conn, "activities", {"id": i, "start_time": f"{day} 07:00:00", "type": typ, "distance_m": km * 1000,
                                "duration_s": km * 360, "elevation_gain_m": 10, "avg_hr": 150}, "id")


def test_weekly_rollup_groups_by_monday_and_ignores_non_runs():
    c = mem()
    run(c, 1, "2026-09-28", 5)   # Mon
    run(c, 2, "2026-10-04", 10)  # Sun, same ISO week
    run(c, 3, "2026-10-05", 8)   # next Mon
    run(c, 4, "2026-10-01", 30, typ="cycling")
    r = {x["period"]: x for x in stats.rollup(c, "week")}
    assert r["2026-09-28"]["km"] == 15 and r["2026-09-28"]["runs"] == 2
    assert r["2026-10-05"]["km"] == 8


def test_ramp_and_upsert_idempotent():
    c = mem()
    for i, d in enumerate(["2026-09-07", "2026-09-14", "2026-09-21", "2026-09-28"]):
        run(c, i, d, 20)
    run(c, 9, "2026-10-05", 30)
    run(c, 9, "2026-10-05", 30)
    assert stats.overview(c, date(2026, 10, 6))["ramp_pct"] == 50.0


def test_mappers():
    a = map_activity({"activityId": 1, "startTimeLocal": "2026-10-01 07:00:00", "activityType": {"typeKey": "running"}, "distance": 5000.0})
    assert a["type"] == "running" and a["distance_m"] == 5000.0
    assert list(map_weights({"dateWeightList": [{"calendarDate": "2026-10-01", "weight": 90500}]}))[0]["weight_kg"] == 90.5
    e = map_export_activity({"activityId": 2, "startTimeLocal": 1759300000000, "activityType": "running", "distance": 500000, "duration": 1800000})
    assert e["distance_m"] == 5000 and e["duration_s"] == 1800


def test_seed_and_packet():
    c = mem()
    seed(c, days=60)
    assert "Last 14 days" in build_packet(c)
    assert stats.weight_series(c)[-1]["avg7"]
