#!/usr/bin/env python3
"""Autopsy zh-CN language pack builder — v2026.12-FINAL.

Extracts every `Bundle.properties-MERGED` belonging to Autopsy itself
(org/sleuthkit/autopsy/**) from the local Autopsy 4.23.1 installation and
generates a complete Bundle_zh_CN.properties skeleton.

Design rules:
  * Never touches the Autopsy installation (read-only scan).
  * Never overwrites an existing translation value: re-running only adds new
    keys from the MERGED template, so expert-team work is preserved.
  * Values are written as ASCII \\uXXXX escapes so the pack loads on Java 8/17/21.
  * Untranslated keys keep their English value and are counted in MANIFEST.json.
"""
from __future__ import annotations

import json
import os
import re
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK_ROOT = HERE.parent
AUTOPSY_ROOT = Path(
    r"E:\Snow\Desktop\workspace\2026\取证\changan-cup-forensics-kit\tools\autopsy"
)
MODULE_ROOT = AUTOPSY_ROOT / "autopsy" / "modules"
TEMPLATE_ROOT = PACK_ROOT / "templates"
LOCALE_ROOT = PACK_ROOT / "locales"
MANIFEST = PACK_ROOT / "MANIFEST.json"

VERSION = "v2026.12-FINAL"
BASELINE = "Autopsy 4.23.1"
ENTRY_RE = re.compile(r"^(org/sleuthkit/autopsy/.*/Bundle)\.properties-MERGED$")


def unescape_prop(value: str) -> str:
    def repl(m: re.Match) -> str:
        return chr(int(m.group(1), 16))
    return re.sub(r"\\u([0-9a-fA-F]{4})", repl, value)


def escape_prop(value: str) -> str:
    out = []
    for ch in value:
        if ch == "\\":
            out.append("\\\\")  # literal backslash must be escaped, or it becomes a line continuation
        elif ord(ch) > 127:
            out.append("\\u%04x" % ord(ch))
        else:
            out.append(ch)
    return "".join(out)


def parse_properties(raw: bytes) -> list[tuple[str, str]]:
    """Minimal .properties reader with backslash line continuation support."""
    text = raw.decode("utf-8", errors="replace")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    logical: list[str] = []
    buf = ""
    for line in lines:
        if buf:
            buf += line.lstrip()
        else:
            buf = line
        if buf.endswith("\\") and not buf.endswith("\\\\"):
            buf = buf[:-1]
            continue
        logical.append(buf)
        buf = ""
    if buf:
        logical.append(buf)

    result: list[tuple[str, str]] = []
    for line in logical:
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("!"):
            continue
        if "=" in s:
            key, value = s.split("=", 1)
        elif ":" in s:
            key, value = s.split(":", 1)
        else:
            key, value = s, ""
        result.append((key.strip(), value.strip().replace("\\\\", "\\")))
    return result


def extract_templates() -> list[tuple[str, str]]:
    """Copy all Autopsy MERGED bundles into templates/. Returns (entry, jar)."""
    found: list[tuple[str, str]] = []
    for jar_path in sorted(MODULE_ROOT.rglob("*.jar")):
        try:
            with zipfile.ZipFile(jar_path) as z:
                for name in z.namelist():
                    m = ENTRY_RE.match(name)
                    if not m:
                        continue
                    rel = m.group(1) + ".properties"
                    dest = TEMPLATE_ROOT / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(z.read(name))
                    found.append((rel, str(jar_path.relative_to(AUTOPSY_ROOT))))
        except (zipfile.BadZipFile, OSError):
            continue
    return found


def build_pack(sources: list[tuple[str, str]]) -> dict:
    report: dict[str, dict] = {}
    total_keys = 0
    total_done = 0

    for rel, jar in sources:
        template = TEMPLATE_ROOT / rel
        keys = parse_properties(template.read_bytes())

        target = LOCALE_ROOT / rel.replace("Bundle.properties", "Bundle_zh_CN.properties")
        target.parent.mkdir(parents=True, exist_ok=True)

        existing: dict[str, str] = {}
        if target.exists():
            existing = dict(parse_properties(target.read_bytes()))

        translated = 0
        lines = [
            "# Autopsy Simplified Chinese language pack - " + VERSION,
            "# Baseline: " + BASELINE,
            "# Source template: templates/" + rel,
            "# Source jar: " + jar,
            "# Untranslated keys keep the English value; update in place.",
            "# Values are \\uXXXX-escaped for Java 8/17/21 compatibility.",
            "",
        ]
        for key, english in keys:
            value = existing.get(key, "")
            # Treat a value identical to English as still untranslated.
            if value and value != english:
                translated += 1
                final = value
            else:
                final = english
            lines.append(key + "=" + escape_prop(unescape_prop(final)))
        target.write_text("\n".join(lines) + "\n", encoding="ascii")

        total_keys += len(keys)
        total_done += translated
        report[rel] = {
            "jar": jar,
            "keys": len(keys),
            "translated": translated,
            "pack": str(target.relative_to(PACK_ROOT)).replace("\\", "/"),
        }

    manifest = {
        "version": VERSION,
        "baseline": BASELINE,
        "generated_by": str(Path(__file__).name),
        "autopsy_root": str(AUTOPSY_ROOT),
        "note": "Read-only scan of Autopsy installation; original jars are never modified by this script.",
        "totals": {
            "bundles": len(sources),
            "keys": total_keys,
            "translated": total_done,
            "coverage_percent": round(100.0 * total_done / total_keys, 2) if total_keys else 0,
        },
        "bundles": report,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    TEMPLATE_ROOT.mkdir(parents=True, exist_ok=True)
    LOCALE_ROOT.mkdir(parents=True, exist_ok=True)
    sources = extract_templates()
    manifest = build_pack(sources)
    t = manifest["totals"]
    print(f"version={VERSION} baseline={BASELINE}")
    print(f"bundles={t['bundles']} keys={t['keys']} translated={t['translated']} coverage={t['coverage_percent']}%")
    print("manifest=" + str(MANIFEST))


if __name__ == "__main__":
    main()
