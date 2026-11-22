# -*- coding: utf-8 -*-
"""导出 platform / cybertriage 待译 bundle 为 JSON 工作文件。"""
import json
import os
import zipfile

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
OUT = r"E:\Snow\Desktop\workspace\2026\取证\决赛备战\autopsy-zhCN-v2026.12-FINAL\translations\batch4"
os.makedirs(OUT, exist_ok=True)

DIALOGS = "platform/modules/org-openide-dialogs.jar"
EXPLORER = "platform/modules/org-openide-explorer.jar"
COREWIN = "platform/modules/org-netbeans-core-windows.jar"
OUTPUT2 = "platform/modules/org-netbeans-core-output2.jar"
UIH = "platform/modules/org-netbeans-modules-uihandler.jar"
OPTAPI = "platform/modules/org-netbeans-modules-options-api.jar"

GROUPS = {
    "dialogs_explorer": (DIALOGS, [
        "org/openide/Bundle.properties",
    ]),
    "explorer": (EXPLORER, [
        "org/openide/explorer/Bundle.properties",
        "org/openide/explorer/propertysheet/Bundle.properties",
        "org/openide/explorer/view/Bundle.properties",
        "org/netbeans/modules/openide/explorer/Bundle.properties",
    ]),
    "corewin": (COREWIN, [
        "org/netbeans/core/windows/Bundle.properties",
        "org/netbeans/core/windows/actions/Bundle.properties",
        "org/netbeans/core/windows/options/Bundle.properties",
        "org/netbeans/core/windows/services/Bundle.properties",
        "org/netbeans/core/windows/view/ui/Bundle.properties",
        "org/netbeans/core/windows/view/ui/toolbars/Bundle.properties",
        "org/netbeans/core/windows/documentgroup/Bundle.properties",
        "org/netbeans/core/windows/persistence/Bundle.properties",
        "org/netbeans/core/windows/resources/Bundle.properties",
        "org/netbeans/core/windows/design/Bundle.properties",
    ]),
    "output2": (OUTPUT2, [
        "org/netbeans/core/output2/Bundle.properties",
        "org/netbeans/core/output2/options/Bundle.properties",
        "org/netbeans/core/output2/ui/Bundle.properties",
    ]),
    "uihandler": (UIH, [
        "org/netbeans/modules/uihandler/Bundle.properties",
        "org/netbeans/modules/exceptions/Bundle.properties",
    ]),
    "options_api": (OPTAPI, [
        "org/netbeans/modules/options/Bundle.properties",
        "org/netbeans/modules/options/classic/Bundle.properties",
        "org/netbeans/modules/options/advanced/Bundle.properties",
        "org/netbeans/modules/options/export/Bundle.properties",
        "org/netbeans/api/options/Bundle.properties",
    ]),
}


def _cont(raw):
    n = 0
    for ch in reversed(raw):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


def parse(txt):
    out, buf = [], None
    for raw in txt.splitlines():
        if buf is not None:
            buf[1] += " " + raw.strip()
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
        k = k.strip()
        if k.startswith("OpenIDE-Module"):
            continue
        if _cont(raw):
            buf = [k, v.strip()]
        else:
            out.append((k, v))
    if buf:
        out.append(tuple(buf))
    return out


for alias, (jar, bundles) in GROUPS.items():
    allitems = []
    with zipfile.ZipFile(os.path.join(ROOT, jar.replace("/", os.sep))) as z:
        for b in bundles:
            txt = z.read(b).decode("utf-8", "replace")
            for k, v in parse(txt):
                allitems.append({"bundle": b, "key": k, "en": v})
    p = os.path.join(OUT, alias + ".json")
    json.dump({"jar": jar, "items": allitems}, open(p, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("%-18s %3d 键 -> %s" % (alias, len(allitems), os.path.basename(p)))
