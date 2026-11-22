#!/usr/bin/env python3
"""Install the v2026.12-FINAL zh-CN language pack into Autopsy 4.23.1.

Safety model (forensic red lines):
  * Original jars are NEVER overwritten in place: each jar is copied to
    backups/ before modification, with its SHA256 recorded.
  * Only Bundle_zh_CN.properties resources are added; no existing entry is
    removed or altered.
  * Rollback is a single command: rollback_pack.py --yes
  * --dry-run prints the plan without writing anything.

Usage:
  python install_pack.py --dry-run
  python install_pack.py
  python install_pack.py --set-locale     # also add -J-Duser.language=zh to autopsy.conf
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK_ROOT = HERE.parent
MANIFEST = PACK_ROOT / "MANIFEST.json"
INSTALL_LOG = PACK_ROOT / "INSTALL_LOG.json"
BACKUP_ROOT = PACK_ROOT / "backups"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def jar_for_bundle(rel: str) -> str:
    return MANIFEST and json.loads(MANIFEST.read_text(encoding="utf-8"))["bundles"][rel]["jar"]


def inject(jar_path: Path, additions: dict[str, Path], dry_run: bool) -> list[str]:
    """Return list of entry names added."""
    added: list[str] = []
    if dry_run:
        return [n for n in additions if True]

    with tempfile.NamedTemporaryFile(prefix="autopsy-i18n-", suffix=".jar", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        with zipfile.ZipFile(jar_path, "r") as src, zipfile.ZipFile(tmp_path, "w") as dst:
            for item in src.infolist():
                if item.filename in additions:
                    continue  # do not keep a stale zh_CN entry
                data = src.read(item.filename)
                zi = zipfile.ZipInfo(item.filename, date_time=item.date_time)
                zi.compress_type = item.compress_type
                zi.external_attr = item.external_attr
                dst.writestr(zi, data)
            for name, source_file in additions.items():
                payload = source_file.read_bytes().replace(b"\r\n", b"\n")
                dst.writestr(name, payload, compress_type=zipfile.ZIP_DEFLATED)
                added.append(name)
        shutil.copystat(jar_path, tmp_path)
        shutil.move(str(tmp_path), str(jar_path))
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return added


def set_locale_flag(conf: Path, backup: Path, dry_run: bool) -> bool:
    text = conf.read_text(encoding="utf-8")
    if "-J-Duser.language=zh" in text:
        return False
    marker = 'default_options="'
    start = text.find(marker)
    if start < 0:
        raise RuntimeError("default_options not found in autopsy.conf")
    end = text.find('"', start + len(marker))
    if end < 0:
        raise RuntimeError("unterminated default_options in autopsy.conf")
    new_text = (
        text[:end]
        + " -J-Duser.language=zh -J-Duser.country=CN"
        + text[end:]
    )
    if not dry_run:
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(conf, backup)
        conf.write_text(new_text, encoding="utf-8")
    return True


def clear_nb_cache(dry: bool = False) -> str:
    """删除 NetBeans 的合并 layer 缓存，否则 jar 内 layer 改动不会被读取。"""
    import os
    from pathlib import Path as _P
    cands = [
        _P(os.environ.get("LOCALAPPDATA", "")) / "autopsy" / "Cache" / "dev",
        _P(os.environ.get("LOCALAPPDATA", "")) / "autopsy" / "Cache",
    ]
    removed = []
    for d in cands:
        if not d.is_dir():
            continue
        if dry:
            removed.append(str(d) + "（dry）")
            continue
        for p in d.glob("*"):
            try:
                if p.is_dir():
                    import shutil as _sh
                    _sh.rmtree(p, ignore_errors=True)
                else:
                    p.unlink()
            except OSError:
                pass
        removed.append(str(d))
    return ", ".join(removed) if removed else "未找到缓存目录"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--root", default=None,
                    help="Autopsy 安装目录（默认取 MANIFEST.autopsy_root 或环境变量 AUTOPSY_HOME）")
    ap.add_argument("--set-locale", action="store_true", help="also switch Autopsy UI language to zh_CN via autopsy.conf (backed up)")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    autopsy_root = Path(args.root or os.environ.get("AUTOPSY_HOME") or manifest["autopsy_root"])
    locale_root = PACK_ROOT / "locales"

    by_jar: dict[str, dict[str, Path]] = {}
    for rel, info in manifest["bundles"].items():
        entry = rel.replace("Bundle.properties", "Bundle_zh_CN.properties")
        pack_file = locale_root / entry
        if not pack_file.exists():
            raise SystemExit(f"missing pack file: {pack_file}")
        by_jar.setdefault(info["jar"], {})[entry] = pack_file

    print(f"[install] version={manifest['version']} baseline={manifest['baseline']}")
    if args.dry_run:
        print("[dry-run] no file will be modified")

    log: dict = {
        "version": manifest["version"],
        "baseline": manifest["baseline"],
        "jars": {},
        "locale_conf_backup": None,
    }
    for jar_rel, additions in sorted(by_jar.items()):
        jar_path = autopsy_root / jar_rel
        if not jar_path.is_file():
            raise SystemExit(f"jar not found: {jar_path}")
        with zipfile.ZipFile(jar_path) as z:
            signed = any(n.startswith("META-INF/") and n.endswith((".SF", ".RSA", ".DSA")) for n in z.namelist())
        if signed:
            print(f"[WARN] {jar_rel} appears signed; injecting resources may break its signature")

        backup = BACKUP_ROOT / jar_rel
        original_hash = sha256(jar_path)
        if not args.dry_run:
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists():
                shutil.copy2(jar_path, backup)
        added = inject(jar_path, additions, args.dry_run)
        print(f"[install] {jar_rel}: +{len(added)} bundles, sha256_before={(sha256(backup) if backup.is_file() else original_hash)[:12]}")
        # 备份文件才是「原始件」，重注入时用它保证 sha256_before 不失真
        pristine = sha256(backup) if backup.is_file() else original_hash
        log["jars"][jar_rel] = {
            "path": str(jar_path),
            "backup": str(backup),
            "sha256_before": pristine,
            "sha256_after": sha256(jar_path) if not args.dry_run else None,
            "entries": sorted(additions),
        }

    if args.set_locale:
        conf = autopsy_root / "AppDataFolder" / "autopsy" / "etc" / "autopsy.conf"
        backup = BACKUP_ROOT / "autopsy.conf"
        if not conf.is_file():
            raise SystemExit(f"autopsy.conf not found: {conf}")
        changed = set_locale_flag(conf, backup, args.dry_run)
        print(f"[install] autopsy.conf locale flag: {'added' if changed else 'already present'}")
        log["locale_conf_backup"] = str(backup) if changed else None

    if not args.dry_run:
        INSTALL_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[install] done. log={INSTALL_LOG}")
        print("[install] restart Autopsy. Rollback: python rollback_pack.py --yes")
    else:
        print("[dry-run] plan only; INSTALL_LOG not written")


if __name__ == "__main__":
    main()
