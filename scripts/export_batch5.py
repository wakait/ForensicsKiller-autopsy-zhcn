# -*- coding: utf-8 -*-
"""导出第五批（打印/快速搜索/多标签/模板/帮助/命令行/core 启动）待译键。"""
import json
import os
import zipfile

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
OUT = r"E:\Snow\Desktop\workspace\2026\取证\决赛备战\autopsy-zhCN-v2026.12-FINAL\translations\batch5"
os.makedirs(OUT, exist_ok=True)

GROUPS = {
    "print": ("platform/modules/org-netbeans-modules-print.jar", [
        "org/netbeans/modules/print/ui/Bundle.properties",
        "org/netbeans/modules/print/action/Bundle.properties",
        "org/netbeans/modules/print/util/Bundle.properties",
    ]),
    "quicksearch": ("platform/modules/org-netbeans-spi-quicksearch.jar", [
        "org/netbeans/modules/quicksearch/Bundle.properties",
        "org/netbeans/modules/quicksearch/web/Bundle.properties",
        "org/netbeans/spi/quicksearch/Bundle.properties",
        "org/netbeans/modules/quicksearch/recent/Bundle.properties",
    ]),
    "misc": ("platform/modules/org-netbeans-core-multitabs.jar", [
        "org/netbeans/core/multitabs/Bundle.properties",
        "org/netbeans/core/multitabs/impl/Bundle.properties",
        "org/netbeans/core/multitabs/prefs/Bundle.properties",
    ]),
    "misc2": ("platform/modules/org-netbeans-modules-javahelp.jar", [
        "org/netbeans/modules/javahelp/Bundle.properties",
    ]),
    "misc3": ("platform/modules/org-netbeans-modules-templates.jar", [
        "org/netbeans/modules/templates/ui/Bundle.properties",
        "org/netbeans/modules/templates/actions/Bundle.properties",
    ]),
    "misc4": ("platform/modules/org-netbeans-modules-sendopts.jar", [
        "org/netbeans/api/sendopts/Bundle.properties",
        "org/netbeans/modules/sendopts/Bundle.properties",
    ]),
    "misc5": ("platform/core/core.jar", [
        "org/netbeans/core/startup/Bundle.properties",
        "org/netbeans/core/startup/impl/Bundle.properties",
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
    items = []
    with zipfile.ZipFile(os.path.join(ROOT, jar.replace("/", os.sep))) as z:
        for b in bundles:
            try:
                txt = z.read(b).decode("utf-8", "replace")
            except KeyError:
                print("  跳过缺失:", b)
                continue
            for k, v in parse(txt):
                items.append({"bundle": b, "key": k, "en": v})
    p = os.path.join(OUT, alias + ".json")
    json.dump({"jar": jar, "items": items}, open(p, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("%-12s %3d 键" % (alias, len(items)))
