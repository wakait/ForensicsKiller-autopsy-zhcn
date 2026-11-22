# -*- coding: utf-8 -*-
"""v4：写入 layer 菜单 displayName（子元素形式），幂等。

要点：
  * layer 中 displayName 是 `<attr name="displayName" .../>` 子元素，不是 folder 的 XML 属性；
  * 判定是否已存在，必须扫描 folder 起始标签后的**属性子元素块**，不能看 XML attrs。
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
BAK = PACK / "backups" / "layerpatch_v4"

NAMES = {
    "Menu/Case": "案件",
    "Menu/File": "文件(&F)",
    "Menu/Edit": "编辑(&E)",
    "Menu/View": "视图(&V)",
    "Menu/GoTo": "导航(&N)",
    "Menu/Tools": "工具(&T)",
    "Menu/Help": "帮助(&H)",
    "Menu/Window": "窗口(&W)",
    "Menu/Window/Tools": "IDE 工具(&T)",
    "Menu/Window/Web": "网页(&W)",
    "Menu/Case/OpenRecentCase": "打开最近的案件",
}

ATTR = re.compile(r'<attr\s+name="([^"]+)"[^>]*/>')


def xesc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def loaded_layers(z):
    mf = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace") \
        if "META-INF/MANIFEST.MF" in z.namelist() else ""
    mf = mf.replace("\r\n", "\n").replace("\n ", "")
    m = re.search(r"OpenIDE-Module-Layer:\s*(\S+)", mf)
    if m:
        return [m.group(1)]
    return ["META-INF/generated-layer.xml"] if "META-INF/generated-layer.xml" in z.namelist() else []


def tag_end(data: bytes, start: int) -> int:
    i, q = start, None
    while i < len(data):
        ch = data[i:i + 1]
        if q:
            if ch == q:
                q = None
        elif ch in (b'"', b"'"):
            q = ch
        elif ch == b">":
            return i + 1
        i += 1
    return -1


def attr_block(data: bytes, pos: int) -> tuple[int, list]:
    """从 folder 起始标签结束后，收集连续的 <attr .../> 子元素。"""
    names, i = [], pos
    while True:
        while i < len(data) and data[i:i + 1].isspace():
            i += 1
        if data[i:i + 5] != b"<attr":
            break
        end = tag_end(data, i)
        if end < 0:
            break
        m = re.match(rb'<attr\s+name="([^"]+)"', data[i:end])
        if not m:
            break
        names.append(m.group(1).decode("utf-8", "replace"))
        i = end
    return i, names


def rewrite(xml: bytes):
    pts = []
    stack = []
    p = expat.ParserCreate("utf-8")

    def start(name, attrs):
        if name != "folder":
            return
        d = dict(attrs)
        stack.append(d.get("name", ""))
        if "/".join(stack) in NAMES:
            pts.append((p.CurrentByteIndex, "/".join(stack)))

    def end(name):
        if name == "folder" and stack:
            stack.pop()

    p.StartElementHandler = start
    p.EndElementHandler = end
    p.Parse(xml, True)

    added = 0
    for start, path in sorted(pts, key=lambda x: -x[0]):
        end = tag_end(xml, start)
        if end < 0:
            continue
        block_end, names = attr_block(xml, end)
        if "displayName" in names:
            continue
        ins = ('<attr name="displayName" stringvalue="%s"/>'
               % xesc(NAMES[path])).encode("utf-8")
        xml = xml[:end] + ins + xml[end:]
        added += 1
    return xml, added


def main():
    if "--restore" in sys.argv:
        n = 0
        for b in BAK.rglob("*.jar"):
            shutil.copy2(b, ROOT / os.path.relpath(b, BAK))
            n += 1
        print("已还原", n)
        return

    dry = "--dry-run" in sys.argv
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
                data, n = rewrite(raw)
                if n:
                    newdata[layer] = data
                    changed += n
            if not changed:
                continue
            print("%-48s 写入 %2d 处" % (os.path.relpath(jp, ROOT), changed))
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
            for _ in range(10):
                try:
                    os.replace(tmp, jp)
                    break
                except PermissionError:
                    time.sleep(1.5)
            else:
                print("     ！替换失败，保留:", tmp.name)
    print("\n合计:", total, "| dry-run" if dry else "| 已写入")


if __name__ == "__main__":
    main()
