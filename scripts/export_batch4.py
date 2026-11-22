# -*- coding: utf-8 -*-
"""导出待译 bundle 的 key=value 到 JSON 工作文件（含价值判定）。"""
import json
import os
import sys
import zipfile

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
OUT = r"E:\Snow\Desktop\workspace\2026\取证\决赛备战\autopsy-zhCN-v2026.12-FINAL\translations\batch4"
os.makedirs(OUT, exist_ok=True)

TARGETS = [
    # (jar, bundle 路径, 别名)
    ("autopsy/modules/ext/sleuthkit-4.15.0.jar", "org/sleuthkit/datamodel/Bundle.properties", "tsk_datamodel"),
    ("autopsy/modules/org-sleuthkit-autopsy-core.jar", "com/basistech/df/cybertriage/autopsy/ctoptions/Bundle.properties", "ct_options"),
    ("autopsy/modules/org-sleuthkit-autopsy-core.jar", "com/basistech/df/cybertriage/autopsy/ctoptions/ctcloud/Bundle.properties", "ct_cloud"),
    ("autopsy/modules/org-sleuthkit-autopsy-core.jar", "com/basistech/df/cybertriage/autopsy/malwarescan/Bundle.properties", "ct_malware"),
    ("autopsy/modules/org-sleuthkit-autopsy-core.jar", "com/basistech/df/cybertriage/autopsy/incidentoptions/Bundle.properties", "ct_incident"),
    ("autopsy/modules/org-sleuthkit-autopsy-core.jar", "com/basistech/df/cybertriage/autopsy/Bundle.properties", "ct_root"),
]


def parse(txt):
    """返回 [(key, value)]，跳过注释；续行合并。"""
    out = []
    buf = None
    for raw in txt.splitlines():
        if buf is not None:
            buf[1] += "\n" + raw
            if not _cont(raw):
                out.append(tuple(buf))
                buf = None
            continue
        s = raw.strip()
        if not s or s.startswith("#") or s.startswith("!"):
            continue
        if "=" not in s:
            continue
        k, v = s.split("=", 1)
        if _cont(raw):
            buf = [k.strip(), v]
        else:
            out.append((k.strip(), v))
    if buf:
        out.append(tuple(buf))
    return out


def _cont(raw):
    n = 0
    for ch in reversed(raw):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


for jar, bundle, alias in TARGETS:
    with zipfile.ZipFile(os.path.join(ROOT, jar.replace("/", os.sep))) as z:
        txt = z.read(bundle).decode("utf-8", "replace")
    items = parse(txt)
    p = os.path.join(OUT, alias + ".json")
    json.dump({"jar": jar, "bundle": bundle, "items": items},
              open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%-14s %3d 键  %s" % (alias, len(items), bundle))
