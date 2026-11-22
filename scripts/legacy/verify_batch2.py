#!/usr/bin/env python3
"""Independent structural verifier for zh_CN bundles against their templates.

For each requested bundle, compares locales/<path>/Bundle_zh_CN.properties with
templates/<path>/Bundle.properties and checks:
  - physical line count parity
  - per-line key order parity (key = left side of first '=', trimmed)
  - duplicate keys
  - key-name pollution (a value containing '<otherkey>=')
  - double unicode escaping (literal backslash-backslash-uXXXX)
  - MessageFormat / printf / accelerator placeholder parity (continuations merged)

Usage:
  python scripts/verify_batch2.py modules/filetypeid modules/fileextmismatch ...
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK = HERE.parent
BASE = Path("org") / "sleuthkit" / "autopsy"
TPL = PACK / "templates" / BASE
LOC = PACK / "locales" / BASE

# Only real formatting placeholders count. '&' mnemonics are intentionally
# excluded: Chinese localization legitimately changes &C -> &复 etc.
PLACEHOLDER = re.compile(r"\{\d+\}|%\d*\$?[sd]")
UNICODE_SEQ = re.compile(r"\\u([0-9a-fA-F]{4})")
DOUBLE_ESC = re.compile(r"\\\\[uU][0-9a-fA-F]{4}")


def load(p: Path) -> list[str]:
    return p.read_text(encoding="utf-8", errors="replace").split("\n")


def key_of(line: str) -> str | None:
    if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
        return None
    return line.split("=", 1)[0].strip()


def _cont(raw_line: str) -> bool:
    """Java properties: a line continues iff it ends with an ODD number of
    backslashes. 'key=\\ ' (escaped space) ends with a space -> NOT a
    continuation, even though rstrip() would reveal a trailing backslash.
    """
    n = 0
    for ch in reversed(raw_line):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


def logical_values(lines: list[str]) -> dict[str, str]:
    """Merge Java-properties continuation lines into logical values."""
    out: dict[str, str] = {}
    i = 0
    n = len(lines)
    while i < n:
        k = key_of(lines[i])
        if k is None:
            i += 1
            continue
        raw = lines[i].split("=", 1)[1]
        # keep joining while the current raw line ends with an odd backslash run
        while _cont(lines[i]) and i + 1 < n:
            raw = raw[:-1] + lines[i + 1].lstrip()
            i += 1
        out[k] = raw
        i += 1
    return out


def decode_uni(s: str) -> str:
    return UNICODE_SEQ.sub(lambda m: chr(int(m.group(1), 16)), s)


def verify(bundle: str) -> dict:
    tp = TPL / bundle / "Bundle.properties"
    lp = LOC / bundle / "Bundle_zh_CN.properties"
    res: dict = {"bundle": bundle, "errors": [], "warnings": []}
    if not tp.exists():
        res["errors"].append(f"template missing: {tp}")
        return res
    if not lp.exists():
        res["errors"].append(f"locale missing: {lp}")
        return res

    tl, ll = load(tp), load(lp)
    res["lines"] = f"{len(ll)}/{len(tl)}"
    if len(ll) != len(tl):
        res["errors"].append(f"line count mismatch {len(ll)} vs {len(tl)}")

    # key order parity, per physical line
    keybad = []
    for idx, (a, b) in enumerate(zip(tl, ll), 1):
        if key_of(a) != key_of(b):
            keybad.append(idx)
    res["key_order_bad"] = len(keybad)
    if keybad:
        res["errors"].append(f"key mismatch at lines {keybad[:12]}")

    # duplicate keys: only flag ones NOT already present in template
    keys = [key_of(l) for l in ll if key_of(l) is not None]
    tpl_keys = [key_of(l) for l in tl if key_of(l) is not None]
    tpl_dup = {k for k in tpl_keys if tpl_keys.count(k) > 1}
    dup = sorted({k for k in keys if keys.count(k) > 1} - tpl_dup)
    res["dup_keys"] = len(dup)
    if dup:
        res["errors"].append(f"duplicate keys (not in template) {dup[:12]}")

    tv, lv = logical_values(tl), logical_values(ll)
    keyset = set(keys)

    # key-name pollution + double escaping
    poll, dbl = 0, 0
    for k, val in lv.items():
        decoded = decode_uni(val)
        for other in keyset:
            if other != k and (other + "=") in decoded:
                poll += 1
                break
        if DOUBLE_ESC.search(val):
            dbl += 1
    res["key_pollution"] = poll
    res["double_escape"] = dbl
    if poll:
        res["errors"].append(f"key pollution in {poll} values")
    if dbl:
        res["errors"].append(f"double-escape in {dbl} values")

    # placeholder parity on merged logical values
    ph_bad = []
    for k in tv:
        if k not in lv:
            continue
        # MessageFormat indexes are absolute; reordering {0}/{1} for Chinese
        # word order is legitimate. Compare as multiset, not sequence.
        a = Counter(PLACEHOLDER.findall(tv[k]))
        b = Counter(PLACEHOLDER.findall(decode_uni(lv[k])))
        if a != b:
            ph_bad.append(k)
    res["placeholder_mismatch"] = len(ph_bad)
    if ph_bad:
        res["errors"].append(f"placeholder mismatch keys {ph_bad[:12]}")

    res["zh_values"] = sum(
        1 for v in lv.values() if re.search(r"[一-鿿]", decode_uni(v))
    )
    return res


def main() -> None:
    bundles = sys.argv[1:]
    if not bundles:
        print("usage: verify_batch2.py <bundle> ...")
        return
    nfail = 0
    for b in bundles:
        r = verify(b)
        ok = not r["errors"]
        flag = "PASS" if ok else "FAIL"
        if not ok:
            nfail += 1
        print(
            f"[{flag}] {r['bundle']:<44} lines={r.get('lines','-'):<10} "
            f"keybad={r.get('key_order_bad','-'):<3} dup={r.get('dup_keys','-'):<3} "
            f"poll={r.get('key_pollution','-'):<3} dbl={r.get('double_escape','-'):<3} "
            f"ph={r.get('placeholder_mismatch','-'):<3} zh={r.get('zh_values','-')}"
        )
        for e in r["errors"]:
            print("        ERROR:", e)
    print(f"\nTOTAL {len(bundles)} bundles, {nfail} FAIL")


if __name__ == "__main__":
    main()
