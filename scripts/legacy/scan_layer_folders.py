# -*- coding: utf-8 -*-
"""扫描 layer.xml：找出靠 localizingBundle 本地化的文件夹名，检查 bundle 里是否有对应键。

NetBeans 规则：folder 的显示名 = 在 localizingBundle 里查「文件夹名」这个 key；
查不到就直接显示文件夹名（英文）。Autopsy 的菜单栏正因此一直是英文。
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
END = re.compile(r"</folder>")
LOCB = re.compile(r'<attr\s+name="SystemFileSystem\.localizingBundle"\s+stringvalue="([^"]+)"')


def scan_layer(xml: str):
    """返回 [(folder_name, bundle_pkg)]，按栈继承 localizingBundle。"""
    out, stack = [], []          # stack: [folder_name, locbundle(or None)]
    cur_loc = None
    for line in xml.split("\n"):
        for m in FOLDER.finditer(line):
            stack.append([m.group(1), cur_loc])
            cur_loc = None
        m = LOCB.search(line)
        if m:
            cur_loc = m.group(1)
            if stack:
                stack[-1][1] = m.group(1)
        if END.search(line) and stack:
            name, loc = stack.pop()
            if loc:
                out.append((name, loc))
            cur_loc = stack[-1][1] if stack else None
    return out


def main():
    want = {}   # (bundle_rel, key) -> [(jar, folder)]
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if not f.endswith(".jar"):
                continue
            jp = os.path.join(dirpath, f)
            try:
                z = zipfile.ZipFile(jp)
            except Exception:
                continue
            for n in z.namelist():
                if not n.endswith("layer.xml"):
                    continue
                try:
                    xml = z.read(n).decode("utf-8", "replace")
                except Exception:
                    continue
                for name, loc in scan_layer(xml):
                    rel = loc.replace(".", "/") + ".properties"
                    want.setdefault((rel, name), []).append((f, n))

    missing, present = [], 0
    for (rel, name), where in sorted(want.items()):
        info = MAN.get(rel)
        if not info:
            missing.append((rel, name, "包未覆盖", where[0][0]))
            continue
        kv, _ = v.parse(PACK / info["pack"])
        if name in kv:
            present += 1
        else:
            missing.append((rel, name, "缺键", where[0][0]))
    print("需要本地化的文件夹名 %d 个：已有键 %d，缺 %d" % (len(want), present, len(missing)))
    for rel, name, why, jar in missing:
        print("  [%s] %-16s %-52s %s" % (why, name[:16], rel, jar[:34]))
    json.dump([{"bundle": r, "key": n, "why": w, "jar": j} for r, n, w, j in missing],
              open(PACK / "QA_LAYER_FOLDERS.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
