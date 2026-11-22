# -*- coding: utf-8 -*-
"""扫描 Autopsy 各模块 class 常量池里的硬编码界面文案（启发式）。

目的：判断「语言包之外」还有多少英文只能改字节码，而不是靠 Bundle。
启发式：含空格、>=2 个英文单词、长度 8~90、不含 = { } % ; < > / \\ ，
排除 SQL、路径、类名、日志格式串。
"""
import json
import os
import re
import struct
import zipfile
from collections import Counter

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
TARGETS = [
    "autopsy/modules/org-sleuthkit-autopsy-core.jar",
    "autopsy/modules/org-sleuthkit-autopsy-keywordsearch.jar",
    "autopsy/modules/org-sleuthkit-autopsy-imagegallery.jar",
    "autopsy/modules/org-sleuthkit-autopsy-recentactivity.jar",
]
BAD = re.compile(r"[={}%;<>/\\\"]|https?://|\.java$|^org\.|^java\.|^com\.|SELECT |INSERT |UPDATE ")
WORDS = re.compile(r"^[A-Z][A-Za-z0-9 ,.\-:!?'()]+$")


def utf8s(data):
    if data[:4] != b"\xca\xfe\xba\xbe":
        return []
    n = struct.unpack(">H", data[8:10])[0]
    i, k, out = 10, 1, []
    while k < n and i < len(data):
        tag = data[i]
        i += 1
        if tag == 1:
            ln = struct.unpack(">H", data[i:i + 2])[0]
            i += 2
            out.append(data[i:i + ln].decode("utf-8", "replace"))
            i += ln
        elif tag in (7, 8, 16, 19, 20):
            i += 2
        elif tag == 15:
            i += 3
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            i += 4
        elif tag in (5, 6):
            i += 8
            k += 1
        else:
            break
        k += 1
    return out


total = 0
report = {}
for jar in TARGETS:
    hits = Counter()
    with zipfile.ZipFile(os.path.join(ROOT, jar.replace("/", os.sep))) as z:
        for name in z.namelist():
            if not name.endswith(".class"):
                continue
            try:
                ss = utf8s(z.read(name))
            except Exception:
                continue
            for s in ss:
                if len(s) < 8 or len(s) > 90 or " " not in s:
                    continue
                if BAD.search(s) or not WORDS.match(s):
                    continue
                if len(s.split()) < 2:
                    continue
                hits[s] += 1
    report[jar] = {"unique": len(hits), "samples": [s for s, _ in hits.most_common(15)]}
    total += len(hits)
    print("%-52s 唯一疑似硬编码 %d" % (jar.split("/")[-1], len(hits)))
    for s in list(hits)[:6]:
        print("     ", s[:78])

json.dump(report, open(r"E:\Snow\Desktop\workspace\2026\取证\决赛备战\autopsy-zhCN-v2026.12-FINAL\QA_HARDCODED.json",
                       "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n合计唯一字符串:", total, "（启发式，含误报）")
