# -*- coding: utf-8 -*-
"""按完整路径把 layer 里的菜单文件夹改名（如 Menu/Help -> Menu/帮助）。

菜单栏文字实测取文件夹名，displayName/bundle 均不生效，故直接改名。
只改「路径完全匹配」的那一个 folder 起标签，不动 Actions/Help 等其它同名节点。

用法：python scripts/rename_menu_folder.py "Menu/Help=帮助" [--root <安装目录>] [--dry-run|--restore]
"""
import os
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path
from xml.parsers import expat

PACK = Path(__file__).resolve().parent.parent
ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
BAK = PACK / "backups" / "rename"


def loaded_layers(z):
    mf = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace") \
        if "META-INF/MANIFEST.MF" in z.namelist() else ""
    mf = mf.replace("\r\n", "\n").replace("\n ", "")
    m = re.search(r"OpenIDE-Module-Layer:\s*(\S+)", mf)
    if m:
        return [m.group(1)]
    return ["META-INF/generated-layer.xml"] if "META-INF/generated-layer.xml" in z.namelist() else []


def rename(xml: bytes, pairs: dict) -> tuple[bytes, int]:
    hits = []
    stack = []
    p = expat.ParserCreate("utf-8")

    def start(name, attrs):
        if name != "folder":
            return
        d = dict(attrs)
        stack.append(d.get("name", ""))
        path = "/".join(stack)
        if path in pairs:
            hits.append((p.CurrentByteIndex, pairs[path]))

    def end(name):
        if name == "folder" and stack:
            stack.pop()

    p.StartElementHandler = start
    p.EndElementHandler = end
    p.Parse(xml, True)

    for start, newname in sorted(hits, key=lambda x: -x[0]):
        m = re.match(rb'<folder\s+name="([^"]+)"', xml[start:])
        if not m:
            continue
        s = start + m.start(1)
        e = start + m.end(1)
        xml = xml[:s] + newname.encode("utf-8") + xml[e:]
    return xml, len(hits)


def main():
    if len(sys.argv) < 2 or "=" not in sys.argv[1]:
        raise SystemExit('用法: "Menu/Help=帮助" [--root ...] [--dry-run|--restore]')
    path, newname = sys.argv[1].split("=", 1)
    if "--root" in sys.argv:
        ROOT = Path(sys.argv[sys.argv.index("--root") + 1])
    else:
        ROOT = Path(r"D:\kit-ascii\autopsy")
    dry = "--dry-run" in sys.argv
    pairs = {path: newname}

    if "--restore" in sys.argv:
        n = 0
        for b in BAK.rglob("*.jar"):
            shutil.copy2(b, ROOT / os.path.relpath(b, BAK))
            n += 1
        print("已还原", n)
        return

    total = 0
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if not f.endswith(".jar"):
                continue
            jp = Path(dirpath) / f
            try:
                z = zipfile.ZipFile(jp)
            except Exception:
                continue
            newdata, changed = {}, 0
            for layer in loaded_layers(z):
                try:
                    raw = z.read(layer)
                except Exception:
                    continue
                data, n = rename(raw, pairs)
                if n:
                    newdata[layer] = data
                    changed += n
            if not changed:
                continue
            print("%-46s 改名 %d 处" % (os.path.relpath(jp, ROOT), changed))
            total += changed
            if dry:
                continue
            b = BAK / os.path.relpath(jp, ROOT)
            b.parent.mkdir(parents=True, exist_ok=True)
            if not b.exists():
                shutil.copy2(jp, b)
            tmp = jp.with_suffix(".tmp")
            with zipfile.ZipFile(jp) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    zout.writestr(item, newdata.get(item.filename, zin.read(item.filename)))
            for _ in range(8):
                try:
                    os.replace(tmp, jp)
                    break
                except PermissionError:
                    time.sleep(1.5)
            else:
                print("   ！替换失败:", tmp.name)
    print("合计:", total, "| dry-run" if dry else "| 已写入")


if __name__ == "__main__":
    main()
