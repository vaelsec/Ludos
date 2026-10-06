import argparse
from datetime import date
from pathlib import Path

from .db import connect


def main():
    p = argparse.ArgumentParser(prog="ludos")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed", help="load synthetic demo data")
    sub.add_parser("serve", help="run the dashboard on localhost:8000")
    s = sub.add_parser("sync", help="pull recent data from Garmin Connect")
    s.add_argument("--days", type=int, default=7)
    i = sub.add_parser("import-export", help="backfill from the Garmin export folder")
    i.add_argument("path")
    sub.add_parser("review-packet", help="write the prompt packet for today's review")
    r = sub.add_parser("save-review", help="store a written review (reads file)")
    r.add_argument("file")
    a = p.parse_args()

    if a.cmd == "seed":
        from .seed import seed
        seed()
    elif a.cmd == "serve":
        import uvicorn
        uvicorn.run("ludos.app:app", host="127.0.0.1", port=8000)
    elif a.cmd == "sync":
        from .sync import sync
        sync(a.days)
    elif a.cmd == "import-export":
        from .importer import import_export
        print(f"imported {import_export(a.path)} activities")
    elif a.cmd == "review-packet":
        from .review import ROOT, build_packet
        out = ROOT / "reviews" / f"packet-{date.today()}.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text(build_packet(connect()))
        print(out)
    elif a.cmd == "save-review":
        from .review import save_review
        save_review(connect(), Path(a.file).read_text())


if __name__ == "__main__":
    main()
