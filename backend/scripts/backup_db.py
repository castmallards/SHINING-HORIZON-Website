"""SQLite backup helper (Phase 7.5).

Creates a timestamped copy of `shining_horizon.db` next to it. Uses SQLite's
online backup API so it's safe to run while the app is serving traffic.

Run:
    cd backend && python -m scripts.backup_db
    cd backend && python -m scripts.backup_db --label pre-launch
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = THIS_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings  # noqa: E402


def _resolve_sqlite_path(database_url: str) -> Path:
    """Strip the sqlite:/// prefix and resolve to an absolute path."""
    if not database_url.startswith("sqlite"):
        raise SystemExit(f"This script only supports SQLite databases. Got: {database_url}")
    # sqlite:///./shining_horizon.db  → ./shining_horizon.db
    path = database_url.split("sqlite:///", 1)[-1]
    p = Path(path)
    if not p.is_absolute():
        p = BACKEND_DIR / p
    return p.resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="Online SQLite backup")
    parser.add_argument("--label", default=None, help="Optional label appended to filename (e.g. 'pre-launch')")
    args = parser.parse_args()

    src = _resolve_sqlite_path(settings.DATABASE_URL)
    if not src.exists():
        raise SystemExit(f"Source DB does not exist: {src}")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    label = f".{args.label}" if args.label else ""
    dst = src.with_name(f"{src.name}.backup-{timestamp}{label}")

    print(f"Backing up: {src}")
    print(f"        ->: {dst}")

    src_conn = sqlite3.connect(str(src))
    dst_conn = sqlite3.connect(str(dst))
    try:
        with dst_conn:
            src_conn.backup(dst_conn)
    finally:
        src_conn.close()
        dst_conn.close()

    size_mb = dst.stat().st_size / (1024 * 1024)
    print(f"Done. Backup size: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
