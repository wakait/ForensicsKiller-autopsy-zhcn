#!/usr/bin/env python
"""List untranslated key=value lines for one or more bundles.

Usage:
    python scripts/list_todo.py <bundle> [<bundle> ...] [--full]

Prints, per key, the line number, whether the value spans continuation lines
(ML = multi-line, must be edited in place to keep line count), and a short
preview of the English value.
"""
import re
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
TPL = PACK / "templates" / "org" / "sleuthkit" / "autopsy"
LOC = PACK / "locales" / "org" / "sleuthkit" / "autopsy"

UNI = re.compile(r"\\u([0-9a-fA-F]{4})")
CJK = re.compile(r"[\u4e00-\u9fff]")


def decode(s: str) -> str:
    return UNI.sub(lambda m: chr(int(m.group(1), 16)), s)


def has_odd_trailing_backslash(line: str) -> bool:
    n = 0
    for ch in reversed(line):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    full = "--full" in sys.argv
    if not args:
        print(__doc__)
        return 2
    grand = 0
    for bundle in args:
        tp = TPL / bundle / "Bundle.properties"
        lp = LOC / bundle / "Bundle_zh_CN.properties"
        if not lp.exists():
            print(f"!! missing {lp}")
            continue
        tl = tp.read_text(encoding="utf-8", errors="replace").split("\n")
        ll = lp.read_text(encoding="utf-8", errors="replace").split("\n")
        print(f"\n===== {bundle}  (tpl={len(tl)} loc={len(ll)}) =====")
        todo = 0
        for i, line in enumerate(ll):
            if "=" not in line or line.lstrip().startswith("#"):
                continue
            raw = line.split("=", 1)[1]
            if CJK.search(decode(raw)):
                continue
            key = line.split("=", 1)[0].strip()
            ml = has_odd_trailing_backslash(line)
            tplval = ""
            if i < len(tl) and "=" in tl[i]:
                tplval = tl[i].split("=", 1)[1]
            val = raw if raw.strip() else tplval
            if not val.strip() and ml:
                j = i + 1
                parts = [raw.rstrip()[:-1]]
                while j < len(ll) and has_odd_trailing_backslash(ll[j - 1]):
                    parts.append(ll[j].strip())
                    j += 1
                val = " ".join(parts)
            todo += 1
            flag = "ML" if ml else "  "
            body = val if full else (val[:110].replace("\n", "\\n"))
            print(f"  L{i+1:5d} {flag} {key} = {body}")
        print(f"  ---- todo={todo}")
        grand += todo
    print(f"\nTOTAL todo = {grand}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
