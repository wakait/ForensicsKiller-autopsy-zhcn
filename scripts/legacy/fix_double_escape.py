#!/usr/bin/env python3
"""Collapse double-escaped \\n / \\t back to single-escaped \n / \t.

Root cause: skeleton generation doubled backslashes, so a newline that should be
"\n" (one backslash) was written as "\\n" (two backslashes). Java .properties then
reads that as the literal two-character text "\n" instead of a line break.

This only collapses a run of EXACTLY TWO backslashes followed by 'n' or 't'.
Runs of 1 (correct newline / continuation) and runs of 4+ (if any) are untouched.
Comments (# ...) are untouched.

Idempotent: after collapse there is a single backslash -> run length 1 -> skipped.
"""
from __future__ import annotations

import sys
from pathlib import Path


def collapse(line: str) -> str:
    if line.lstrip().startswith("#"):
        return line
    out = []
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue
        # count backslash run
        j = i
        while j < n and line[j] == "\\":
            j += 1
        run = j - i
        nxt = line[j] if j < n else ""
        if run == 2 and nxt in ("n", "t"):
            out.append("\\" + nxt)
            i = j + 1
        else:
            out.append(line[i:j])
            i = j
    return "".join(out)


def main() -> None:
    targets = sys.argv[1:]
    if not targets:
        print("usage: fix_double_escape.py <file> ...")
        return
    total = 0
    for t in targets:
        p = Path(t)
        lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
        new = [collapse(l) for l in lines]
        k = sum(1 for a, b in zip(lines, new) if a != b)
        if k:
            p.write_text("\n".join(new), encoding="ascii")
            total += k
            print(f"{t}: {k} lines collapsed")
    print(f"total {total} lines across {len(targets)} files")


if __name__ == "__main__":
    main()
