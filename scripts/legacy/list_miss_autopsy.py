# -*- coding: utf-8 -*-
"""列出 autopsy/ 目录下未覆盖的 bundle，并统计有效键数与英文样本。"""
import json
import os
import re
import zipfile

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
PACK = r"E:\Snow\Desktop\workspace\2026\取证\决赛备战\autopsy-zhCN-v2026.12-FINAL"
data = json.load(open(os.path.join(PACK, "QA_ALL_MODULES.json"), encoding="utf-8"))

rows = data["rows"]
autopsy_miss = [r for r in rows if "bundle" in r and not r["covered"]
                and r["jar"].startswith("autopsy/")]

CJK = re.compile(r"[\u4e00-\u9fff]")
KEY = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*=(.*)$")


def read_entry(jar, name):
    with zipfile.ZipFile(os.path.join(ROOT, jar.replace("/", os.sep))) as z:
        return z.read(name).decode("utf-8", "replace")


total_keys = 0
for r in sorted(autopsy_miss, key=lambda x: -x["size"]):
    txt = read_entry(r["jar"], r["bundle"])
    keys = [m.group(2) for line in txt.splitlines() if (m := KEY.match(line))]
    ui = [k for k in keys if len(k.strip()) > 2 and not CJK.search(k)]
    total_keys += len(ui)
    print("\n%-58s %-4d键 %s" % (r["jar"].split("/")[-1], len(ui), r["bundle"]))
    for s in ui[:6]:
        print("    |", s[:110])
print("\n合计可译键:", total_keys)
