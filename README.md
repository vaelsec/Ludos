# ludos

Local running/fitness dashboard built on Garmin data (Forerunner 965, Index S2, HR strap, Stryd).
Python + SQLite + FastAPI, Chart.js frontend. Runs on localhost; personal data never leaves the machine.

## Quick start
    python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
    python -m ludos seed            # demo data (LUDOS_DB=path to use a separate db)
    python -m ludos serve           # http://127.0.0.1:8000

## Real data
    python -m ludos import-export /path/to/garmin-export   # 9-year backfill (verify units first, see ludos/importer.py)
    GARMIN_EMAIL=... GARMIN_PASSWORD=... python -m ludos sync --days 7   # daily sync; tokens cached in .garmin_tokens/

## Daily review
    python -m ludos review-packet   # writes reviews/packet-DATE.md (metrics + context/context.md)
    # in a Claude Code session: read the packet, write the review, then:
    python -m ludos save-review review.md

Copy `context/context.example.md` to `context/context.md` and fill it in.
`data/`, `reviews/`, `exports/`, `.env`, tokens and `context/context.md` are git-ignored.
