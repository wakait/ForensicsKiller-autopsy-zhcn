#!/usr/bin/env python3
"""Roll back the v2026.12-FINAL language pack injection.

Restores every jar recorded in INSTALL_LOG.json from its backup and verifies
that the original SHA256 is recovered. Requires --yes to actually write.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK_ROOT = HERE.parent
INSTALL_LOG = PACK_ROOT / "INSTALL_LOG.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yes", action="store_true", help="required to perform the rollback")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not INSTALL_LOG.exists():
        raise SystemExit("no INSTALL_LOG.json found - nothing was installed by this pack")
    log = json.loads(INSTALL_LOG.read_text(encoding="utf-8"))

    if not (args.yes or args.dry_run):
        raise SystemExit("refusing to roll back without --yes (use --dry-run to preview)")

    failures = 0
    for jar_rel, info in log["jars"].items():
        target = Path(info["path"])
        backup = Path(info["backup"])
        expected = info["sha256_before"]
        if not backup.is_file():
            print(f"[FAIL] backup missing: {backup}")
            failures += 1
            continue
        actual_backup = sha256(backup)
        if actual_backup != expected:
            print(f"[FAIL] backup hash mismatch for {jar_rel}: {actual_backup[:12]} != {expected[:12]}")
            failures += 1
            continue
        print(f"[rollback] {jar_rel}: backup verified {expected[:12]}")
        if not args.dry_run:
            shutil.copy2(backup, target)
            after = sha256(target)
            if after != expected:
                print(f"[FAIL] restore hash mismatch for {jar_rel}: {after[:12]}")
                failures += 1
            else:
                print(f"[rollback] restored {jar_rel}: {after[:12]}")

    conf_backup = log.get("locale_conf_backup")
    if conf_backup:
        backup = Path(conf_backup)
        first_jar = Path(log["jars"][next(iter(log["jars"]))]["path"])
        auto_root = first_jar.parents[2]  # .../tools/autopsy
        conf = auto_root / "AppDataFolder" / "autopsy" / "etc" / "autopsy.conf"
        if not backup.is_file():
            print(f"[FAIL] autopsy.conf backup missing: {backup}")
            failures += 1
        else:
            print(f"[rollback] autopsy.conf backup found: {backup}")
            if not args.dry_run:
                shutil.copy2(backup, conf)
                print(f"[rollback] restored {conf}")

    if args.dry_run:
        print("[dry-run] no file was modified")
    elif failures:
        print(f"[rollback] FINISHED WITH {failures} FAILURE(S) - inspect manually")
        raise SystemExit(1)
    else:
        print("[rollback] all jars restored to their original SHA256")
        INSTALL_LOG.rename(INSTALL_LOG.with_suffix(".json.rolled-back"))


if __name__ == "__main__":
    main()
