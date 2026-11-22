# -*- coding: utf-8 -*-
"""按 156 个 bundle 重算 MANIFEST totals。"""
import json
import re
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
MAN = PACK / "MANIFEST.json"
UNI = re.compile(r"\\u([0-9a-fA-F]{4})")
man = json.loads(MAN.read_text(encoding="utf-8"))

keys = translated = 0
for rel, info in man["bundles"].items():
    p = PACK / info["pack"]
    txt = p.read_text(encoding="utf-8", errors="replace")
    t = UNI.sub(lambda m: chr(int(m.group(1), 16)), txt)
    n = 0
    for line in t.split("\n"):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("!"):
            continue
        n += 1
    cjk = sum(1 for line in t.split("\n")
              if "=" in line and any("\u4e00" <= c <= "\u9fff" for c in line))
    info["keys"] = n
    info["translated"] = cjk
    keys += n
    translated += cjk

man["totals"].update({
    "bundles": len(man["bundles"]),
    "keys": keys,
    "translated": translated,
    "coverage_percent": round(100.0 * translated / keys, 2),
    "batch4_note": "Batch 4: 新增 30 个 bundle —— TSK 数据模型(462)、NetBeans 平台层(openide-dialogs/explorer/core-windows/output2/uihandler/options-api，共 811)、Cyber Triage 选项(127)；并修复 90 行『值已折叠但旧英文续行残留』的垃圾键。",
})
MAN.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
print("bundles=%d keys=%d translated=%d coverage=%.2f%%"
      % (len(man["bundles"]), keys, translated, 100.0 * translated / keys))
