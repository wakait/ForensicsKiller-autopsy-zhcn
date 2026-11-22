#!/usr/bin/env python3
r"""Canonicalize pack escaping against the template (one-shot, no rebuild).

For each key:
  * if the decoded zh value equals the decoded template value, restore the
    template's exact raw escape form;
  * otherwise decode the zh value with Java .properties rules and re-encode it
    canonically (\\ -> \, \uXXXX for non-ASCII, \n for newline, \  for leading space).
This removes both over-escaping and under-escaping without a rebuild cycle.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK_ROOT = HERE.parent
MANIFEST = PACK_ROOT / "MANIFEST.json"


def raw_pairs(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    logical: list[str] = []
    buf = ""
    for line in text.split("\n"):
        buf = buf + line.lstrip() if buf else line
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
        out.append((k.strip(), v.strip()))
    return out


_HEX = re.compile(r"[0-9a-fA-F]{4}$")


def decode(s: str) -> str:
    out: list[str] = []
    i = 0
    simple = {"n": "\n", "t": "\t", "r": "\r", "f": "\f"}
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == "u" and i + 6 <= len(s) and _HEX.match(s[i + 2:i + 6]):
                out.append(chr(int(s[i + 2:i + 6], 16)))
                i += 6
            elif nxt in simple:
                out.append(simple[nxt])
                i += 2
            else:
                out.append(nxt)
                i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def encode(s: str) -> str:
    out: list[str] = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\f":
            out.append("\\f")
        elif ord(ch) > 127:
            out.append("\\u%04x" % ord(ch))
        else:
            out.append(ch)
    val = "".join(out)
    if val.startswith(" "):
        val = "\\ " + val[1:]
    return val


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed = 0
    translations = 0
    for rel, info in manifest["bundles"].items():
        tp = PACK_ROOT / "templates" / rel
        pp = PACK_ROOT / info["pack"]
        template = raw_pairs(tp)
        pack = dict(raw_pairs(pp))
        known = {k for k, _ in template}
        lines = [
            "# Autopsy Simplified Chinese language pack - " + manifest["version"],
            "# Baseline: " + manifest["baseline"],
            "# Source template: templates/" + rel,
            "# Source jar: " + info["jar"],
            "# Canonical Java .properties escaping; untranslated keys keep template form.",
            "",
        ]
        for key, raw_en in template:
            raw_zh = pack.get(key, "")
            dec_en = decode(raw_en)
            dec_zh = decode(raw_zh)
            translated = bool(dec_zh) and dec_zh != dec_en
            # Reject any residual embedded-key pollution.
            m = re.match(r"([A-Za-z][A-Za-z0-9_.]*)\s*=", dec_zh)
            if m and m.group(1) in known:
                translated = False
            final_raw = encode(dec_zh) if translated else raw_en
            if final_raw != raw_zh:
                changed += 1
            if translated:
                translations += 1
            lines.append(key + "=" + final_raw)
        pp.write_text("\n".join(lines) + "\n", encoding="ascii")
    print(f"canonicalized {changed} raw values; translations={translations}")
    print("read-only verification only: do NOT rerun build_pack.py or repair_pack.py")


if __name__ == "__main__":
    main()
