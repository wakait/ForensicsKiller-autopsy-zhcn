#!/usr/bin/env python3
"""Diagnose verifier FAILs: template-side dups and exact placeholder token diffs."""
from __future__ import annotations

import sys
from pathlib import Path
import verify_batch2 as v


def dups(lines: list[str]) -> list[str]:
    ks = [v.key_of(l) for l in lines if v.key_of(l) is not None]
    return sorted({k for k in ks if ks.count(k) > 1})


def main() -> None:
    for b in sys.argv[1:]:
        tp = v.TPL / b / "Bundle.properties"
        lp = v.LOC / b / "Bundle_zh_CN.properties"
        tl, ll = v.load(tp), v.load(lp)
        print("=" * 70)
        print("BUNDLE", b)
        td, ld = dups(tl), dups(ll)
        print("  template dups:", td)
        print("  locale   dups:", ld)
        print("  dups introduced by translation:", [k for k in ld if k not in td])
        tv, lv = v.logical_values(tl), v.logical_values(ll)
        ph_bad = []
        for k in tv:
            if k not in lv:
                continue
            a = v.PLACEHOLDER.findall(tv[k])
            btoks = v.PLACEHOLDER.findall(v.decode_uni(lv[k]))
            if a != btoks:
                ph_bad.append((k, a, btoks, tv[k].strip()[:90], v.decode_uni(lv[k]).strip()[:90]))
        print("  placeholder mismatches:", len(ph_bad))
        for k, a, btoks, en, zh in ph_bad[:25]:
            print(f"    - {k}")
            print(f"        EN tokens={a}  :: {en!r}")
            print(f"        ZH tokens={btoks}  :: {zh!r}")


if __name__ == "__main__":
    main()
