#!/usr/bin/env python3
"""Compare backslash-n / backslash-t escape level: template vs zh value, per key.

Java .properties semantics at the SOURCE-TEXT level:
  \n  -> newline char      (single backslash + n)
  \\n -> literal "\\n" text (double backslash + n)  <-- defect if template had \n
We count runs of backslashes immediately before n/t in raw source text.
"""
from __future__ import annotations

import sys
import re
from pathlib import Path
import verify_batch2 as v

# runs of backslashes followed by n or t
RUN = re.compile(r"(\\+)([nt])")


def profile(s: str) -> dict[str, int]:
    c: dict[str, int] = {}
    for m in RUN.finditer(s):
        level = len(m.group(1))
        key = f"{'\\' * level}{m.group(2)}"
        c[key] = c.get(key, 0) + 1
    return c


def main() -> None:
    grand = 0
    for b in sys.argv[1:]:
        tp = v.TPL / b / "Bundle.properties"
        lp = v.LOC / b / "Bundle_zh_CN.properties"
        if not tp.exists() or not lp.exists():
            print("MISSING", b)
            continue
        tv, lv = v.logical_values(v.load(tp)), v.logical_values(v.load(lp))
        bad = []
        for k, zhraw in lv.items():
            en = profile(tv.get(k, ""))
            zh = profile(zhraw)
            # expected: same set of single \n/\t occurrences as template
            en_single = en.get("\\n", 0) + en.get("\\t", 0)
            zh_single = zh.get("\\n", 0) + zh.get("\\t", 0)
            zh_double = zh.get("\\\\n", 0) + zh.get("\\\\t", 0)
            if zh_double > 0 or (en_single > 0 and zh_single != en_single):
                bad.append((k, en, zh))
        if bad:
            print(f"=== {b}: {len(bad) } key(s) with escape-level concern ===")
            for k, en, zh in bad[:15]:
                print(f"   {k}")
                print(f"      EN profile={en}")
                print(f"      ZH profile={zh}")
            grand += len(bad)
    print(f"\nTOTAL concern keys: {grand}")


if __name__ == "__main__":
    main()
