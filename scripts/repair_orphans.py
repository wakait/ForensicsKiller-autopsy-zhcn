# -*- coding: utf-8 -*-
"""修复「值已折叠为单行、旧续行残留」的垃圾键。

判定：某行不含 '='，且上一行不是奇数反斜杠续行 → 该行是孤儿（Java 会把它当成空值键）。
只删除满足下列之一的孤儿行：
  * 缩进开头（>=2 空格）
  * 或含 >=3 个英文单词
其余情况只报告，不改。
"""
import json
import re
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
WORD = re.compile(r"[A-Za-z]{3,}")


def _cont(raw):
    n = 0
    for ch in reversed(raw):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


def clean(text: str):
    lines = text.split("\n")
    out, dropped, kept = [], [], []
    prev_cont = False
    for raw in lines:
        body = raw.rstrip("\r")
        s = body.strip()
        is_kv = "=" in s and not s.startswith("#") and not s.startswith("!")
        if prev_cont:
            out.append(body)
            prev_cont = _cont(body)
            continue
        if s and not s.startswith("#") and not s.startswith("!") and not is_kv:
            indented = body[:2] == "  "
            words = len(WORD.findall(s))
            bare_key = re.fullmatch(r"[A-Za-z0-9_.\-]+", s) is not None
            if indented or words >= 3 or s.startswith("\\") or not bare_key:
                dropped.append(body)
                continue
            kept.append(body)
        out.append(body)
        prev_cont = _cont(body) if is_kv or s else False
    return "\n".join(out), dropped, kept


def main():
    rows = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))["bundles"]
    total = 0
    for rel, info in sorted(rows.items()):
        p = PACK / info["pack"]
        text = p.read_text(encoding="utf-8", errors="replace")
        new, dropped, kept = clean(text)
        if dropped:
            p.write_text(new, encoding="utf-8")
            total += len(dropped)
            print("%-58s 删除孤儿行 %d" % (rel.split("/")[-2], len(dropped)))
        if kept:
            print("   [保留待查] %s: %s" % (rel, kept[:2]))
    print("\n共删除孤儿行:", total)


if __name__ == "__main__":
    main()
