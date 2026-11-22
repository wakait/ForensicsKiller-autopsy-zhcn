#!/usr/bin/env python3
"""Escape ALL non-ASCII chars on every non-comment line (handles continuation lines).

The prior escape_values.py only converted the right side of a line containing '='.
For multi-line values written with trailing-backslash continuation, the continuation
lines carry Chinese text but contain no '=', so they were left as raw UTF-8 -- which
breaks Java .properties (ISO-8859-1) loading.

This script is safe because:
  - Java .properties keys and comments here are pure ASCII.
  - Comments (# lines) are skipped untouched.
  - Continuation lines are value fragments, so escaping all their non-ASCII is correct.
It is idempotent: already-escaped \\uXXXX sequences are pure ASCII and untouched.
"""
from __future__ import annotations

import sys
from pathlib import Path


def escape_all(line: str) -> str:
    if line.lstrip().startswith("#"):
        return line
    return "".join("\\u%04x" % ord(ch) if ord(ch) > 127 else ch for ch in line)


def main() -> None:
    targets = sys.argv[1:]
    if not targets:
        print("usage: escape_all.py <file> ...")
        return
    changed = 0
    for t in targets:
        p = Path(t)
        lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
        new = [escape_all(l) for l in lines]
        n = sum(1 for a, b in zip(lines, new) if a != b)
        if n:
            p.write_text("\n".join(new), encoding="ascii")
            changed += n
            print(f"{t}: {n} lines escaped")
    print(f"total {changed} lines across {len(targets)} files")


if __name__ == "__main__":
    main()
