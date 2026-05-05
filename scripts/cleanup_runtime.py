from __future__ import annotations

import argparse
import os
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean old logs and public media files.")
    parser.add_argument("--log-days", type=float, default=float(os.getenv("CLEANUP_LOG_DAYS", "14")), help="Delete logs older than this many days.")
    parser.add_argument("--public-hours", type=float, default=float(os.getenv("CLEANUP_PUBLIC_HOURS", "48")), help="Delete public/media files older than this many hours.")
    parser.add_argument("--dry-run", action="store_true", help="Print files that would be deleted.")
    args = parser.parse_args()

    now = time.time()
    deleted = 0
    deleted += cleanup(ROOT_DIR / "logs", now - args.log_days * 86400, args.dry_run)
    deleted += cleanup_file(ROOT_DIR / "errorLog.txt", now - args.log_days * 86400, args.dry_run)
    deleted += cleanup(ROOT_DIR / "public" / "media", now - args.public_hours * 3600, args.dry_run)
    print(f"cleanup complete: {deleted} file(s) {'matched' if args.dry_run else 'deleted'}")
    return 0


def cleanup(root: Path, cutoff: float, dry_run: bool) -> int:
    if not root.exists():
        return 0
    count = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            if path.stat().st_mtime > cutoff:
                continue
            count += 1
            if dry_run:
                print(path)
            else:
                path.unlink()
        except OSError as exc:
            print(f"skip {path}: {exc}")
    return count


def cleanup_file(path: Path, cutoff: float, dry_run: bool) -> int:
    if not path.exists() or not path.is_file():
        return 0
    try:
        if path.stat().st_mtime > cutoff:
            return 0
        if dry_run:
            print(path)
        else:
            path.unlink()
        return 1
    except OSError as exc:
        print(f"skip {path}: {exc}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
