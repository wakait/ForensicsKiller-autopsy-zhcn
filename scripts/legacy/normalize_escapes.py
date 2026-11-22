#!/usr/bin/env python3
r"""One-shot normalizer for over-escaped backslash runs in the zh-CN pack.

Repeated build/repair cycles had doubled escape sequences (e.g. 8 backslashes
before 'n' instead of the template's 2). This script reduces every over-long
run to the canonical form without touching \uXXXX escapes or key names.

DO NOT follow this with build_pack.py unless you have first verified with
qa_pack.py that no further doubling occurs.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK_ROOT = HERE.parent
MANIFEST = PACK_ROOT / "MANIFEST.json"


def normalize(text: str) -> tuple[str, int]:
    changes = 0

    def repl(m: re.Match) -> str:
        nonlocal changes
        run = m.group(1)
        tail = m.string[m.end():m.end() + 5]
        if re.match(r"u[0-9a-fA-F]{4}", tail):
            wanted = "\\"
        else:
            wanted = "\\\\" if len(run) >= 2 else "\\"
        if run != wanted:
            changes += 1
        return wanted

    out = re.sub(r"(\\+)", repl, text)
    return out, changes


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    total = 0
    for rel, info in manifest["bundles"].items():
        path = PACK_ROOT / info["pack"]
        text = path.read_text(encoding="ascii")
        new, n = normalize(text)
        if n:
            path.write_text(new, encoding="ascii")
            total += n
    print(f"normalized {total} over-escaped runs across {len(manifest['bundles'])} bundles")
    print("read-only verification required; do NOT rerun build_pack.py without checking qa_pack.py first")


if __name__ == "__main__":
    main()
