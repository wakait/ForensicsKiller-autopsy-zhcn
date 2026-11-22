#!/usr/bin/env python3
r"""Finalize the zh-CN pack without any escape transformation (one shot).

Fixes only:
  1. over-doubled escaped spaces (`\\ ` -> `\ `);
  2. embedded-key pollution (value begins with the next key name and '=');
  3. key order differing from template.

Raw values are otherwise copied verbatim from the current pack (translations)
or from the template (untranslated). No decode/re-encode is performed.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_pack import parse_properties

PACK_ROOT = HERE.parent
MANIFEST = PACK_ROOT / "MANIFEST.json"


def read_raw(path: Path) -> list[tuple[str, str]]:
    lines = path.read_text(encoding="ascii", errors="replace").split("\n")
    logical: list[str] = []
    buf = ""
    for line in lines:
        raw = line
        if buf:
            buf += raw.lstrip()
        else:
            buf = raw
        # continuation only when the RAW line ends with an odd number of backslashes
        m = re.search(r"(\\+)$", buf)
        if m and len(m.group(1)) % 2 == 1:
            buf = buf[:-1]
            continue
        logical.append(buf)
        buf = ""
    if buf:
        logical.append(buf)
    out: list[tuple[str, str]] = []
    for line in logical:
        s = line.strip()
        if not s or s[0] in "#!":
            continue
        if "=" in s:
            k, v = s.split("=", 1)
        elif ":" in s:
            k, v = s.split(":", 1)
        else:
            k, v = s, ""
        # preserve escaped space: strip() would turn `\ ` into `\` (continuation)
        out.append((k.strip(), v.strip()))
    return out


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixes = 0
    for rel, info in manifest["bundles"].items():
        tp = PACK_ROOT / "templates" / rel
        pp = PACK_ROOT / info["pack"]
        template_keys = [k for k, _ in parse_properties(tp.read_bytes())]
        template_raw = dict(read_raw(tp))
        known = set(template_keys)

        values: dict[str, list[str]] = defaultdict(list)
        for k, v in read_raw(pp):
            v = v.replace("\\\\ ", "\\ ")  # undo doubled escaped space only
            m = re.match(r"([A-Za-z][A-Za-z0-9_.]*)\s*=", v)
            if m and m.group(1) in known:
                fixes += 1
                values[k].append(v[:m.start()])
                values[m.group(1)].append(v[m.end():])
            else:
                values[k].append(v)

        cursors: dict[str, int] = defaultdict(int)
        lines = [
            "# Autopsy Simplified Chinese language pack - " + manifest["version"],
            "# Baseline: " + manifest["baseline"],
            "# Source template: templates/" + rel,
            "# Source jar: " + info["jar"],
            "# Untranslated keys keep the template escape form.",
            "",
        ]
        for key in template_keys:
            i = cursors[key]
            q = values.get(key, [])
            cand = q[i] if i < len(q) else ""
            cursors[key] = i + 1
            raw_en = template_raw.get(key, "")
            final = cand if cand and cand != raw_en else raw_en
            lines.append(key + "=" + final)
        pp.write_text("\n".join(lines) + "\n", encoding="ascii")
    print(f"finalized {len(manifest['bundles'])} bundles; split {fixes} polluted entries")


if __name__ == "__main__":
    main()
