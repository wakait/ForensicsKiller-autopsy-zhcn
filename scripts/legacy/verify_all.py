#!/usr/bin/env python3
"""Run verify_batch2 over every bundle in the pack; print only failures + summary."""
from __future__ import annotations

from pathlib import Path
import verify_batch2 as v

def main() -> None:
    bundles = []
    for tp in v.TPL.rglob("Bundle.properties"):
        rel = tp.relative_to(v.TPL)
        bundles.append(str(rel.parent))
    bundles.sort()
    fails = 0
    for b in bundles:
        r = v.verify(b)
        if r["errors"]:
            fails += 1
            print(f"[FAIL] {b}: {r['errors']}")
    print(f"\nchecked {len(bundles)} bundles, {fails} FAIL")

if __name__ == "__main__":
    main()
