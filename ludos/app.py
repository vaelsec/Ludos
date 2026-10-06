from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import stats
from .db import connect

app = FastAPI(title="Ludos")
STATIC = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/overview")
def overview():
    return stats.overview(connect())


@app.get("/api/rollup")
def rollup(period: str = "week", since: str | None = None):
    try:
        return stats.rollup(connect(), period, since)
    except ValueError:
        raise HTTPException(400, "period must be day, week or month")


@app.get("/api/weight")
def weight(since: str | None = None):
    return stats.weight_series(connect(), since)


@app.get("/api/daily")
def daily(since: str | None = None):
    rows = connect().execute("SELECT * FROM daily WHERE date >= ? ORDER BY date", (since or "0000",)).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/review")
def review():
    r = connect().execute("SELECT date, text FROM reviews ORDER BY date DESC LIMIT 1").fetchone()
    return dict(r) if r else None
