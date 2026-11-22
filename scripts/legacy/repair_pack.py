#!/usr/bin/env python3
"""Repair corrupted entries in the generated zh-CN pack.

Corruption pattern (introduced by manual edits on lines whose English value
was a continuation marker): a key's value begins with the NEXT key name and
its '=', e.g.
    AllCasesSearchDialog.errorLabel.text=AllCasesSearchDialog.correlationTypeLabel.text=\u7c7b...

This script uses templates/ as the authority for key order, recovers the
displaced Chinese value into its proper key, and rewrites every pack file.
It is idempotent and never touches templates/ or the Autopsy installation.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_pack import MANIFEST, PACK_ROOT, escape_prop, parse_properties, unescape_prop

REPORT = PACK_ROOT / "REPAIR_REPORT.json"


def split_embedded(value: str, known_keys: set[str]) -> tuple[str, str | None, str]:
    """Return (own_value, embedded_key, embedded_value)."""
    for m in re.finditer(r"([A-Za-z][A-Za-z0-9_.]*)\s*=", value):
        candidate = m.group(1)
        if candidate in known_keys and candidate:
            return value[:m.start()], candidate, value[m.end():]
    return value, None, ""


def repair() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixes: list[dict] = []

    for rel, info in manifest["bundles"].items():
        template_path = PACK_ROOT / "templates" / rel
        pack_path = PACK_ROOT / info["pack"]
        template_pairs = parse_properties(template_path.read_bytes())
        template_keys = [k for k, _ in template_pairs]
        known = set(template_keys)

        # values_by_key is a queue so duplicate keys keep their positions.
        values: dict[str, list[str]] = defaultdict(list)
        for line in pack_path.read_text(encoding="ascii", errors="replace").replace("\r\n", "\n").split("\n"):
            s = line.strip()
            if not s or s.startswith("#") or s.startswith("!"):
                continue
            if "=" not in s:
                if s in known:
                    values[s].append("")
                continue
            key, value = s.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key not in known:
                continue
            own, embedded, tail = split_embedded(unescape_prop(value), known)
            if embedded:
                fixes.append({
                    "bundle": rel,
                    "polluted_key": key,
                    "embedded_key": embedded,
                    "recovered_value": tail[:80],
                })
                values[key].append(own)
                values[embedded].append(tail)
            else:
                values[key].append(value)

        cursors: dict[str, int] = defaultdict(int)
        lines: list[str] = []
        for key, english in template_pairs:
            idx = cursors[key]
            queue = values.get(key, [])
            candidate = queue[idx] if idx < len(queue) else ""
            cursors[key] = idx + 1
            # Accept the recovered value only if it is not English and not empty.
            if candidate and candidate != unescape_prop(english):
                final = candidate
            else:
                final = english
            lines.append(key + "=" + escape_prop(unescape_prop(final)))

        pack_path.write_text("\n".join(lines) + "\n", encoding="ascii")

    report = {
        "version": manifest["version"],
        "fixes": fixes,
        "fix_count": len(fixes),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"repaired {len(fixes)} corrupted entries across {len(manifest['bundles'])} bundles")
    for f in fixes[:20]:
        print(f"  {f['bundle'].split('/autopsy/')[-1]}: {f['polluted_key']} <- {f['embedded_key']}")
    print("report=" + str(REPORT))
    return report


if __name__ == "__main__":
    repair()
