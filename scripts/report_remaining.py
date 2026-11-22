# -*- coding: utf-8 -*-
"""列出仍未中文化的值，并按「可保留」类别归因，剩下的就是真缺口。"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_new as v  # noqa

PACK = Path(__file__).resolve().parent.parent
CJK = re.compile(r"[\u4e00-\u9fff]")
UNI = re.compile(r"\\u([0-9a-fA-F]{4})")


def dec(s):
    return UNI.sub(lambda m: chr(int(m.group(1), 16)), s)


def classify(val, key):
    t = dec(val).strip()
    if not t:
        return "空值"
    if t.lower() in ("true", "false"):
        return "布尔配置"
    if re.fullmatch(r"[A-Za-z0-9_\-]+", t) and not t[0].isupper():
        return "配置取值"
    if re.search(r"(?i)(ctrl|shift|alt|\bcmd\b|\bmeta\b)", t) and len(t) <= 24:
        return "快捷键"
    if t in ("N/A", "n/a", "null", "NONE", "None"):
        return "占位"
    if re.fullmatch(r"[\W_]+", t):
        return "纯符号"
    if re.match(r"^https?://", t):
        return "URL"
    if re.fullmatch(r"[A-Za-z0-9_./\\-]+\.(png|gif|jpg|jar|properties|xml|txt|log)", t):
        return "文件名"
    if t.isupper() and len(t) <= 14 and " " not in t:
        return "常量/枚举"
    return "待译"


def main():
    rows = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))["bundles"]
    cats = Counter()
    todo = []
    for rel, info in sorted(rows.items()):
        kv, _ = v.parse(PACK / info["pack"])
        for k, val in kv.items():
            t = dec(val)
            if CJK.search(t):
                continue
            c = classify(val, k)
            cats[c] += 1
            if c == "待译":
                todo.append({"bundle": rel, "key": k, "en": t})
    print("未中文化总数:", sum(cats.values()))
    for c, n in cats.most_common():
        print("  %-10s %d" % (c, n))
    json.dump(todo, open(PACK / "QA_TODO.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\n真缺口(待译):", len(todo))
    for x in todo[:25]:
        print("   %-46s %-34s %s" % (x["bundle"].split("/")[-2][:46], x["key"][:34], x["en"][:54]))


if __name__ == "__main__":
    main()
