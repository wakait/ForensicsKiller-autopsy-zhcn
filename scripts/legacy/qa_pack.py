#!/usr/bin/env python3
"""QA check for the zh-CN pack: key integrity, translation coverage, placeholder safety."""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK_ROOT = HERE.parent
MANIFEST = PACK_ROOT / "MANIFEST.json"
REPORT = PACK_ROOT / "QA_REPORT.json"

PLACEHOLDER_PATTERNS = [
    re.compile(r"\{\d+\}"),
    re.compile(r"%[sdf]"),
]


def parse(raw: bytes) -> dict[str, str]:
    """Same continuation handling as build_pack.py, so key counts are comparable."""
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    logical: list[str] = []
    buf = ""
    for line in text.split("\n"):
        buf = buf + line.lstrip() if buf else line
        if buf.endswith("\\") and not buf.endswith("\\\\"):
            buf = buf[:-1]
            continue
        logical.append(buf)
        buf = ""
    if buf:
        logical.append(buf)

    out: dict[str, str] = {}
    for line in logical:
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("!"):
            continue
        if "=" in s:
            k, v = s.split("=", 1)
        elif ":" in s:
            k, v = s.split(":", 1)
        else:
            k, v = s, ""
        out[k.strip()] = v.strip().replace("\\\\", "\\")
    return out


def unescape(s: str) -> str:
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)


def tokens(s: str) -> list[str]:
    """Compare only value-bearing placeholders. HTML tags, '&' mnemonics and
    literal backslashes are excluded: localizing tag text is legitimate and
    otherwise generates false positives."""
    out: list[str] = []
    for p in PLACEHOLDER_PATTERNS:
        out.extend(p.findall(s))
    return sorted(out)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    issues: list[dict] = []
    coverage: dict[str, dict] = {}
    total_keys = total_done = 0

    for rel, info in manifest["bundles"].items():
        template = parse((PACK_ROOT / "templates" / rel).read_bytes())
        pack_path = PACK_ROOT / info["pack"]
        pack = parse(pack_path.read_bytes())

        missing = sorted(set(template) - set(pack))
        extra = sorted(set(pack) - set(template))
        done = 0
        for key, english in template.items():
            value = unescape(pack.get(key, ""))
            source = unescape(english)
            if value and value != source:
                done += 1
                if tokens(source) != tokens(value):
                    issues.append({
                        "bundle": rel,
                        "key": key,
                        "issue": "placeholder_mismatch",
                        "english": source[:120],
                        "chinese": value[:120],
                    })
        if missing or extra:
            issues.append({
                "bundle": rel,
                "issue": "key_set_mismatch",
                "missing": missing[:20],
                "extra": extra[:20],
            })
        coverage[rel] = {
            "keys": len(template),
            "translated": done,
            "percent": round(100.0 * done / len(template), 2) if template else 0,
        }
        total_keys += len(template)
        total_done += done

    report = {
        "version": manifest["version"],
        "baseline": manifest["baseline"],
        "totals": {
            "bundles": len(coverage),
            "keys": total_keys,
            "translated": total_done,
            "coverage_percent": round(100.0 * total_done / total_keys, 2) if total_keys else 0,
        },
        "issue_count": len(issues),
        "issues": issues[:200],
        "per_bundle": coverage,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"QA version={report['version']} keys={total_keys} translated={total_done} "
          f"coverage={report['totals']['coverage_percent']}% issues={len(issues)}")
    print("report=" + str(REPORT))


if __name__ == "__main__":
    main()
