# -*- coding: utf-8 -*-
"""把一份 zh_*.json 落成语言包资源：
  templates/<bundle 路径>/Bundle.properties      （从 jar 原样复制，作对照基线）
  locales/<bundle 路径>/Bundle_zh_CN.properties  （逐键替换，未译键原样保留）
  MANIFEST.json 增加 bundles 条目

用法：python scripts/add_bundle.py translations/batch4/zh_tsk.json [...]
"""
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
PACK = Path(__file__).resolve().parent.parent
MANIFEST = PACK / "MANIFEST.json"


def _cont(raw):
    n = 0
    for ch in reversed(raw):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


def esc(s):
    return "".join("\\u%04x" % ord(c) if ord(c) > 127 else c for c in s)


def build(jar_rel, bundle_rel, zh_map):
    """按模板逐行生成 locale，返回 (keys, translated)。"""
    jp = ROOT / jar_rel.replace("/", os.sep)
    with zipfile.ZipFile(jp) as z:
        raw = z.read(bundle_rel)

    tpl = PACK / "templates" / bundle_rel
    tpl.parent.mkdir(parents=True, exist_ok=True)
    tpl.write_bytes(raw)

    text = raw.decode("latin-1")          # .properties 原始字节按 latin-1 透传
    out, keys, translated = [], 0, 0
    i = 0
    lines = text.split("\n")
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("!"):
            out.append(line.rstrip("\r"))
            i += 1
            continue
        # 收集逻辑行（含续行）
        block = [line]
        while _cont(lines[i].rstrip("\r")) and i + 1 < len(lines):
            i += 1
            block.append(lines[i])
        i += 1
        if "=" not in block[0]:
            out.extend(b.rstrip("\r") for b in block)
            continue
        key = block[0].split("=", 1)[0].strip()
        keys += 1
        if key in zh_map:
            out.append("%s=%s" % (key, esc(zh_map[key])))
            if any(ord(c) > 127 for c in zh_map[key]):
                translated += 1
        else:
            out.extend(b.rstrip("\r") for b in block)

    # 模板中没有的新键（如菜单路径键）追加到末尾
    existing = set()
    for line in out:
        t = line.strip()
        if "=" in t and not t.startswith("#"):
            existing.add(t.split("=", 1)[0].strip())
    extra = [k for k in zh_map if k not in existing]
    for k in extra:
        out.append("%s=%s" % (k, esc(zh_map[k])))

    loc = PACK / "locales" / os.path.dirname(bundle_rel) / "Bundle_zh_CN.properties"
    loc.parent.mkdir(parents=True, exist_ok=True)
    loc.write_text("\n".join(out) + "\n", encoding="utf-8")
    return keys + len(extra), translated + len(extra), tpl, loc


JAR_BY_PREFIX = [
    ("org/openide/explorer/", "platform/modules/org-openide-explorer.jar"),
    ("org/netbeans/modules/openide/explorer/", "platform/modules/org-openide-explorer.jar"),
    ("org/openide/", "platform/modules/org-openide-dialogs.jar"),
    ("org/netbeans/core/windows/", "platform/modules/org-netbeans-core-windows.jar"),
    ("org/netbeans/core/output2/", "platform/modules/org-netbeans-core-output2.jar"),
    ("org/netbeans/modules/uihandler/", "platform/modules/org-netbeans-modules-uihandler.jar"),
    ("org/netbeans/modules/exceptions/", "platform/modules/org-netbeans-modules-uihandler.jar"),
    ("org/netbeans/modules/options/", "platform/modules/org-netbeans-modules-options-api.jar"),
    ("org/netbeans/api/options/", "platform/modules/org-netbeans-modules-options-api.jar"),
    ("org/netbeans/modules/print/", "platform/modules/org-netbeans-modules-print.jar"),
    ("org/netbeans/modules/quicksearch/", "platform/modules/org-netbeans-spi-quicksearch.jar"),
    ("org/netbeans/spi/quicksearch/", "platform/modules/org-netbeans-spi-quicksearch.jar"),
    ("org/netbeans/core/multitabs/", "platform/modules/org-netbeans-core-multitabs.jar"),
    ("org/netbeans/modules/javahelp/", "platform/modules/org-netbeans-modules-javahelp.jar"),
    ("org/netbeans/modules/templates/", "platform/modules/org-netbeans-modules-templates.jar"),
    ("org/netbeans/api/sendopts/", "platform/modules/org-netbeans-modules-sendopts.jar"),
    ("org/netbeans/modules/sendopts/", "platform/modules/org-netbeans-modules-sendopts.jar"),
    ("org/netbeans/core/ui/resources/", "platform/modules/org-netbeans-core-ui.jar"),
    ("org/netbeans/modules/favorites/", "platform/modules/org-netbeans-modules-favorites.jar"),
    ("org/netbeans/core/startup/", "platform/core/core.jar"),
    ("com/basistech/", "autopsy/modules/org-sleuthkit-autopsy-core.jar"),
    ("org/sleuthkit/datamodel/", "autopsy/modules/ext/sleuthkit-4.15.0.jar"),
]


def resolve_jar(bundle_rel, hinted=None):
    if hinted:
        return hinted
    for pre, jar in JAR_BY_PREFIX:
        if bundle_rel.startswith(pre):
            return jar
    raise SystemExit("无法确定 jar: " + bundle_rel)


def main():
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.is_absolute():
            p = PACK / p
        d = json.loads(p.read_text(encoding="utf-8"))
        groups = {}
        for it in d["items"]:
            b = it.get("bundle") or d.get("bundle")
            groups.setdefault(b, {})[it["key"]] = it["zh"]
        for bundle_rel, zh in groups.items():
            jar = resolve_jar(bundle_rel, d.get("jar"))
            keys, translated, tpl, loc = build(jar, bundle_rel, zh)
            man["bundles"][bundle_rel] = {
                "jar": jar.replace("/", "\\"),
                "keys": keys,
                "translated": translated,
                "pack": str(loc.relative_to(PACK)).replace("\\", "/"),
            }
            print("%-62s %3d 键  %3d 中文化" % (bundle_rel, keys, translated))
    MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    print("MANIFEST bundles 总数:", len(man["bundles"]))


if __name__ == "__main__":
    main()
