#!/usr/bin/env python3
"""Escape non-ASCII characters in VALUE side only (safe, idempotent).

For each line: split at the FIRST '=', convert only the right-hand side's
non-ASCII chars to \\uXXXX. Key names, line count, order, backslashes,
continuation markers and comments are preserved byte-for-byte.

This deliberately does NOT parse Java .properties semantics. It is the only
sanctioned way to convert agent-authored UTF-8 translations into the frozen
pack format.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK_ROOT = HERE.parent
MANIFEST = PACK_ROOT / "MANIFEST.json"


def escape_line(line: str) -> str:
    if "=" not in line or line.lstrip().startswith("#"):
        return line
    key, val = line.split("=", 1)
    out = "".join("\\u%04x" % ord(ch) if ord(ch) > 127 else ch for ch in val)
    return key + "=" + out


def main() -> None:
    targets = sys.argv[1:]
    if not targets:
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        targets = [info["pack"] for info in m["bundles"].values()]
    changed = 0
    for t in targets:
        p = Path(t)
        if not p.is_absolute():
            p = PACK_ROOT / p
        lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
        new = [escape_line(l) for l in lines]
        n = sum(1 for a, b in zip(lines, new) if a != b)
        if n:
            p.write_text("\n".join(new), encoding="ascii")
            changed += n
    print(f"escaped non-ASCII values in {changed} lines across {len(targets)} files")


if __name__ == "__main__":
    main()
