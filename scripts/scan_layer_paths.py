# -*- coding: utf-8 -*-
"""按「路径键」扫描菜单/文件夹显示名缺口。

NetBeans：文件夹显示名 = 在 localizingBundle 里查该文件夹的完整路径（如 Menu/View）。
"""
import json
import os
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_new as v  # noqa

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
PACK = Path(__file__).resolve().parent.parent
MAN = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))["bundles"]

FOLDER = re.compile(r'<folder\s+name="([^"]+)"')
LOCB = re.compile(r'<attr\s+name="SystemFileSystem\.localizingBundle"\s+stringvalue="([^"]+)"')


def scan(xml):
    out, stack, pending = [], [], None
    for line in xml.split("\n"):
        for m in FOLDER.finditer(line):
            path = "/".join([s[0] for s in stack] + [m.group(1)])
            stack.append([m.group(1), None, path])
        m = LOCB.search(line)
        if m and stack:
            stack[-1][1] = m.group(1)
        if "</folder>" in line and stack:
            name, loc, path = stack.pop()
            if loc:
                out.append((path, loc))
    return out


def main():
    want = {}
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if not f.endswith(".jar"):
                continue
            try:
                z = zipfile.ZipFile(os.path.join(dirpath, f))
            except Exception:
                continue
            for n in z.namelist():
                if not n.endswith("layer.xml"):
                    continue
                try:
                    xml = z.read(n).decode("utf-8", "replace")
                except Exception:
                    continue
                for path, loc in scan(xml):
                    rel = loc.replace(".", "/") + ".properties"
                    want[(rel, path)] = f

    miss, ok = [], 0
    for (rel, path), jar in sorted(want.items()):
        info = MAN.get(rel)
        if not info:
            miss.append({"bundle": rel, "key": path, "why": "包未覆盖", "jar": jar})
            continue
        kv, _ = v.parse(PACK / info["pack"])
        if path in kv and any("\u4e00" <= c <= "\u9fff"
                              for c in re.sub(r"\\u([0-9a-fA-F]{4})",
                                              lambda m: chr(int(m.group(1), 16)), kv[path])):
            ok += 1
        elif path in kv:
            miss.append({"bundle": rel, "key": path, "why": "键存在但未译", "jar": jar})
        else:
            miss.append({"bundle": rel, "key": path, "why": "缺键", "jar": jar})
    print("需本地化路径键 %d：已译 %d，待处理 %d" % (len(want), ok, len(miss)))
    for m in miss:
        print("  [%-6s] %-46s %-46s %s" % (m["why"], m["key"][:46], m["bundle"][:46], m["jar"][:26]))
    json.dump(miss, open(PACK / "QA_LAYER_FOLDERS.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
