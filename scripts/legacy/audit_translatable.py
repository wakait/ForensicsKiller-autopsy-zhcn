#!/usr/bin/env python
"""Audit *translatable* English strings, filtering out non-translatable tokens.

A value counts as translatable when it looks like human-readable prose:
  * contains at least one run of >=3 Latin letters, AND
  * contains at least two whitespace-separated word-ish chunks (>=2 letters each),
    or ends with sentence punctuation ('.', ':', '?', '!')
AND is not: empty, pure number/format, URL/path, font name, single-token
identifier (CoreComponents, jButton2, SHA1), or mnemonic letter.

Usage:
    python scripts/audit_translatable.py [bundle ...] [--list] [--top N]
"""
import re
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
TPL = PACK / "templates" / "org" / "sleuthkit" / "autopsy"
LOC = PACK / "locales" / "org" / "sleuthkit" / "autopsy"

UNI = re.compile(r"\\u([0-9a-fA-F]{4})")
CJK = re.compile(r"[\u4e00-\u9fff]")
WORD = re.compile(r"[A-Za-z]{3,}")
WORD2 = re.compile(r"[A-Za-z]{2,}")

NON_TRANSLATABLE_KEYS = ("mnemonic", "AccessibleContext.accessibleName.JButton", "font.name")
FONT_NAMES = {
    "Dialog", "DialogInput", "Monospaced", "Serif", "SansSerif", "Helvetica",
    "Helvetica-Oblique", "Helvetica-Bold", "Helvetica-BoldOblique", "Times-Italic",
    "Times-Bold", "Times-BoldItalic", "Times-Roman", "Courier", "Courier-Oblique",
    "Courier-Bold", "Courier-BoldOblique",
}
ACRONYMS = {"SHA1", "SHA-256", "MD5", "MB", "GB", "KB", "TB", "HTML", "XML", "CSV",
            "JSON", "PDF", "URL", "URI", "NaN", "OK", "ID", "IP", "UTC", "GMT"}


def decode(s: str) -> str:
    return UNI.sub(lambda m: chr(int(m.group(1), 16)), s)


def translatable(key: str, val: str) -> bool:
    v = val.strip()
    if not v:
        return False
    if any(k in key for k in NON_TRANSLATABLE_KEYS):
        return False
    if v in FONT_NAMES or v in ACRONYMS:
        return False
    if "http://" in v or "https://" in v or "file://" in v:
        return False
    if re.fullmatch(r"[\d\s:/.\-+]+", v):          # pure numbers / ratios
        return False
    if re.fullmatch(r"[A-Za-z0-9_./:\\-]+", v):     # single path/identifier token
        return False
    if not WORD.search(v):
        return False
    words = [w for w in WORD2.findall(v)]
    if len(words) < 2 and not v.rstrip().endswith((".", ":", "?", "!")):
        return False
    return True


def odd_trailing_backslash(line: str) -> bool:
    n = 0
    for ch in reversed(line):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


def scan(bundle: str):
    tp = TPL / bundle / "Bundle.properties"
    lp = LOC / bundle / "Bundle_zh_CN.properties"
    if not lp.exists():
        return None
    tl = tp.read_text(encoding="utf-8", errors="replace").split("\n") if tp.exists() else []
    ll = lp.read_text(encoding="utf-8", errors="replace").split("\n")
    done = todo = 0
    items = []
    for i, line in enumerate(ll):
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key = line.split("=", 1)[0].strip()
        raw = line.split("=", 1)[1]
        ml = odd_trailing_backslash(line)
        tplval = ""
        if i < len(tl) and "=" in tl[i]:
            tplval = tl[i].split("=", 1)[1]
        base = tplval if tplval.strip() else raw
        if ml:
            j = i + 1
            parts = [base.rstrip()[:-1]]
            while j < len(ll) and odd_trailing_backslash(ll[j - 1]):
                parts.append(ll[j].strip())
                j += 1
            base = " ".join(parts)
        english = decode(base)
        if not translatable(key, english):
            continue
        translated = bool(CJK.search(decode(raw)))
        todo += 1
        items.append((i + 1, key, english[:120], ml, translated))
        if translated:
            done += 1
    return dict(bundle=bundle, done=done, todo=todo, items=items)


def main() -> int:
    want_list = "--list" in sys.argv
    argv = sys.argv[1:]
    top = None
    if "--top" in argv:
        idx = argv.index("--top")
        top = int(argv[idx + 1])
        del argv[idx:idx + 2]
    args = [a for a in argv if not a.startswith("--")]
    if top:
        args = args or None
    bundles = args or [str(p.relative_to(TPL).parent) for p in TPL.rglob("Bundle.properties")
                       if (LOC / p.relative_to(TPL).parent / "Bundle_zh_CN.properties").exists()]
    rows = []
    for b in bundles:
        r = scan(b)
        if r:
            rows.append(r)
    rows.sort(key=lambda r: -(r["todo"] - r["done"]))
    gd = sum(r["done"] for r in rows)
    gt = sum(r["todo"] for r in rows)
    shown = rows[:top] if top else rows
    if top:
        print(f"{'bundle':<46}{'done':>6}{'total':>7}{'left':>6}   pct")
        for r in shown:
            left = r["todo"] - r["done"]
            if left == 0:
                continue
            pct = 100.0 * r["done"] / r["todo"] if r["todo"] else 100.0
            print(f"{r['bundle']:<46}{r['done']:>6}{r['todo']:>7}{left:>6}  {pct:5.1f}%")
    if want_list:
        for r in shown:
            left = [(l, k, e, m, t) for (l, k, e, m, t) in r["items"] if not t]
            if not left:
                continue
            print(f"\n===== {r['bundle']}  done={r['done']}/{r['todo']} =====")
            for l, k, e, m, t in left:
                print(f"  L{l:5d} {'ML' if m else '  '} {k} = {e}")
    print(f"\nTRANSLATABLE TOTAL: {gt}   done: {gd}   left: {gt - gd}"
          f"   coverage: {100.0 * gd / gt if gt else 100:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
