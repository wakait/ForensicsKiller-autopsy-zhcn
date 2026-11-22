# -*- coding: utf-8 -*-
"""解析 class 常量池字符串，确认 BundleProvider / ICEpdf 的 Locale 用法。"""
import os
import struct
import zipfile

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))


def const_strings(data):
    """极简 class 文件常量池解析，返回 CONSTANT_Utf8 列表。"""
    out = []
    if data[:4] != b"\xca\xfe\xba\xbe":
        return out
    n = struct.unpack(">H", data[8:10])[0]
    i = 10
    k = 1
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
        elif tag in (15,):
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


def dump(jar, cls):
    with zipfile.ZipFile(os.path.join(ROOT, jar.replace("/", os.sep))) as z:
        data = z.read(cls)
    ss = const_strings(data)
    print("\n### %s :: %s" % (jar.split("/")[-1], cls))
    for s in ss:
        if any(w in s for w in ("Bundle", "Locale", "getBundle", "zh", "ENGLISH",
                                "ROOT", "ResourceBundle", "properties")):
            print("   ", s)


dump("autopsy/modules/ext/sleuthkit-4.15.0.jar",
     "org/sleuthkit/datamodel/BundleProvider.class")
dump("autopsy/modules/ext/icepdf-viewer-6.2.2.jar",
     "org/icepdf/ri/resources/MessageBundle.class")
