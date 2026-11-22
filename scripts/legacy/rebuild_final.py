#!/usr/bin/env python3
r"""Definitive line-preserving rebuild (run once, no further rebuild scripts).

For each bundle, copy the template file line-for-line. Only the value after
'=' is replaced when the current pack contains a non-empty, different value
for that key. Key order, continuation lines, and template escaping are kept
exactly as shipped by Autopsy.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK_ROOT = HERE.parent
MANIFEST = PACK_ROOT / "MANIFEST.json"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    translated_total = 0
    for rel, info in manifest["bundles"].items():
        tp = PACK_ROOT / "templates" / rel
        pp = PACK_ROOT / info["pack"]

        current: dict[str, str] = {}
        for line in pp.read_text(encoding="ascii", errors="replace").split("\n"):
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                k = k.strip()
                if k and k not in current:
                    current[k] = v.strip()

        out: list[str] = []
        count = 0
        for line in tp.read_text(encoding="ascii", errors="replace").split("\n"):
            if "=" not in line or line.startswith("#"):
                out.append(line)
                continue
            k, en = line.split("=", 1)
            key = k.strip()
            zh = current.get(key, "").strip()
            if zh and zh != en.strip() and not zh.startswith(key + "="):
                out.append(k + "=" + zh)
                count += 1
            else:
                out.append(line)
        pp.write_text("\n".join(out), encoding="ascii")
        translated_total += count
    print(f"line-preserving rebuild done; translations={translated_total}")
    print("VERIFY ONLY: do not run build_pack.py / repair_pack.py / canonicalize_pack.py / finalize_pack.py again")


if __name__ == "__main__":
    main()
