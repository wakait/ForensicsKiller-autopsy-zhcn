# -*- coding: utf-8 -*-
"""按值术语表把 tsk / cybertriage 的 items 译成 zh，输出 zh_*.json；报告未覆盖值。"""
import glob
import json
import os

BASE = r"E:\Snow\Desktop\workspace\2026\取证\决赛备战\autopsy-zhCN-v2026.12-FINAL\translations\batch4"

gloss = {}
for f in ("gloss_a.tsv", "gloss_b.tsv"):
    for line in open(os.path.join(BASE, f), encoding="utf-8"):
        line = line.rstrip("\n")
        if "|||" not in line:
            continue
        en, zh = line.split("|||", 1)
        gloss[en.lstrip("\ufeff")] = zh
print("术语表条目:", len(gloss))

srcs = ["tsk_datamodel.json"] + sorted(
    os.path.basename(p) for p in glob.glob(os.path.join(BASE, "ct_*.json")))
missing = {}
total = done = 0
for s in srcs:
    p = os.path.join(BASE, s)
    d = json.load(open(p, encoding="utf-8"))
    out = []
    for k, en in d["items"]:
        total += 1
        zh = gloss.get(en)
        if zh is None:
            missing.setdefault(en, []).append((s, k))
            zh = en
        else:
            done += 1
        out.append({"key": k, "en": en, "zh": zh})
    dst = os.path.join(BASE, "zh_" + s.replace("tsk_datamodel", "tsk"))
    json.dump({"jar": d["jar"], "bundle": d["bundle"], "items": out},
              open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("  %-22s %3d 条 -> %s" % (s, len(out), os.path.basename(dst)))

print("\n总条目 %d，已译 %d，未覆盖 %d 个不同值" % (total, done, len(missing)))
for en, where in sorted(missing.items(), key=lambda kv: -len(kv[1]))[:20]:
    print("  [%dx] %r" % (len(where), en[:80]))
