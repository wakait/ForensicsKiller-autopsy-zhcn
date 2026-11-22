#!/usr/bin/env python
"""Apply a {key: chinese_value} mapping to a locale bundle, preserving structure.

Usage:
    python scripts/apply_translations.py <bundle> <mapping.json> [--dry-run]

Rules:
  * Only the value part (after the first '=') on the matching line is replaced.
  * Keys whose English value spans continuation lines are SKIPPED (line count
    must stay identical to the template, and collapsing them would change it).
  * Chinese is written literally (UTF-8); run scripts/escape_all.py afterwards.
  * Keys present in mapping but absent in the file are reported, nothing written.
"""
import json
import re
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
TPL = PACK / "templates" / "org" / "sleuthkit" / "autopsy"
LOC = PACK / "locales" / "org" / "sleuthkit" / "autopsy"

CJK = re.compile(r"[\u4e00-\u9fff]")


def odd_trailing_backslash(line: str) -> bool:
    n = 0
    for ch in reversed(line):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


def main() -> int:
    dry = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        return 2
    bundle, mapfile = args
    lp = LOC / bundle / "Bundle_zh_CN.properties"
    tp = TPL / bundle / "Bundle.properties"
    if not lp.exists():
        print(f"!! missing {lp}")
        return 3
    mapping = json.loads(Path(mapfile).read_text(encoding="utf-8"))
    lines = lp.read_text(encoding="utf-8", errors="replace").split("\n")
    tpl = tp.read_text(encoding="utf-8", errors="replace").split("\n") if tp.exists() else []

    seen = set()
    app = skip_ml = 0
    out = list(lines)
    for i, line in enumerate(lines):
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key = line.split("=", 1)[0].strip()
        if key not in mapping:
            continue
        if odd_trailing_backslash(line):
            skip_ml += 1
            seen.add(key)
            print(f"  SKIP(ML) L{i+1} {key}")
            continue
        if i < len(tpl) and "=" in tpl[i] and odd_trailing_backslash(tpl[i]):
            # template says this value continues; keep layout untouched
            skip_ml += 1
            seen.add(key)
            print(f"  SKIP(TPL-ML) L{i+1} {key}")
            continue
        newval = mapping[key]
        if not CJK.search(newval):
            print(f"  WARN(no-chinese) L{i+1} {key} -> {newval!r}")
        out[i] = line.split("=", 1)[0] + "=" + newval
        seen.add(key)
        app += 1

    missing = [k for k in mapping if k not in seen]
    if not dry:
        lp.write_text("\n".join(out), encoding="utf-8")
    print(f"[{bundle}] applied={app} skipped_ml={skip_ml} missing_keys={len(missing)}"
          f"{' (dry-run)' if dry else ''}")
    for k in missing[:10]:
        print(f"  MISSING {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
