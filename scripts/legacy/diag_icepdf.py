# -*- coding: utf-8 -*-
"""找出 ICEpdf 中引用 MessageBundle 的类；并查谁 require 了 ICEpdf 模块。"""
import os
import struct
import zipfile

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))


def const_strings(data):
    out = []
    if data[:4] != b"\xca\xfe\xba\xbe":
        return out
    n = struct.unpack(">H", data[8:10])[0]
    i, k = 10, 1
    while k < n:
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


jp = os.path.join(ROOT, r"autopsy\modules\ext\icepdf-viewer-6.2.2.jar")
with zipfile.ZipFile(jp) as z:
    hits = []
    for n in z.namelist():
        if not n.endswith(".class"):
            continue
        try:
            ss = const_strings(z.read(n))
        except Exception:
            continue
        if any("icepdf/ri/resources/MessageBundle" in s for s in ss):
            hits.append(n)
    print("引用 MessageBundle 的类(%d):" % len(hits))
    for h in hits[:12]:
        print("  ", h)
    loc = [s for s in const_strings(z.read(hits[0])) if "Locale" in s or "getBundle" in s]
    print("  首个类的 Locale 相关常量:", loc[:8])

print("\n=== 哪些模块 require ICEpdf ===")
for dirpath, _, files in os.walk(os.path.join(ROOT, "autopsy", "modules")):
    for f in files:
        if not f.endswith(".jar"):
            continue
        p = os.path.join(dirpath, f)
        try:
            with zipfile.ZipFile(p) as z:
                mf = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace") \
                    if "META-INF/MANIFEST.MF" in z.namelist() else ""
        except Exception:
            continue
        if "icepdf" in mf.lower() or "icepdf" in f.lower():
            print("  ", os.path.relpath(p, ROOT))
