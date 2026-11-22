# -*- coding: utf-8 -*-
"""1) 检查 jar 是否含签名文件（修改会导致模块加载失败）
2) 检查 TSK / ICEpdf 的 bundle 加载方式（类内是否引用 Bundle）
3) 统计 platform 模块可译键数，按可见性排序
"""
import os
import re
import zipfile

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))

TARGETS = [
    "platform/modules/org-netbeans-core-windows.jar",
    "platform/modules/org-netbeans-core-ui.jar",
    "platform/modules/org-netbeans-core.jar",
    "platform/modules/org-netbeans-modules-options-api.jar",
    "platform/modules/org-netbeans-modules-uihandler.jar",
    "platform/modules/org-netbeans-core-output2.jar",
    "platform/modules/org-netbeans-modules-print.jar",
    "platform/modules/org-netbeans-modules-autoupdate-ui.jar",
    "platform/modules/org-openide-explorer.jar",
    "platform/modules/org-netbeans-spi-quicksearch.jar",
    "autopsy/modules/ext/sleuthkit-4.15.0.jar",
    "autopsy/modules/ext/icepdf-viewer-6.2.2.jar",
    "autopsy/modules/org-sleuthkit-autopsy-core.jar",
]

print("=== 签名检查 ===")
for t in TARGETS:
    p = os.path.join(ROOT, t.replace("/", os.sep))
    with zipfile.ZipFile(p) as z:
        sig = [n for n in z.namelist()
               if re.match(r"META-INF/[^/]+\.(SF|RSA|DSA|EC)$", n)]
    print("%-58s %s" % (t.split("/")[-1], ("签名:" + ",".join(sig)) if sig else "未签名"))

print("\n=== TSK bundle 引用检查 ===")
with zipfile.ZipFile(os.path.join(ROOT, r"autopsy\modules\ext\sleuthkit-4.15.0.jar")) as z:
    names = [n for n in z.namelist() if n.endswith(".class")]
    hit = 0
    for n in names:
        raw = z.read(n)
        if b"org/sleuthkit/datamodel/Bundle" in raw or b"Bundle.properties" in raw:
            print("  引用:", n)
            hit += 1
            if hit >= 5:
                break
    if not hit:
        print("  未在 class 常量池发现 Bundle 引用（可能用 ResourceBundle 动态拼接）")

print("\n=== platform 可译键统计 ===")
KEY = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*=(.*)$")
CJK = re.compile(r"[\u4e00-\u9fff]")
for t in TARGETS[:10]:
    p = os.path.join(ROOT, t.replace("/", os.sep))
    with zipfile.ZipFile(p) as z:
        bs = [n for n in z.namelist() if n.endswith("Bundle.properties")]
        tot = 0
        for b in bs:
            txt = z.read(b).decode("utf-8", "replace")
            for line in txt.splitlines():
                m = KEY.match(line)
                if m and len(m.group(2).strip()) > 2 and not CJK.search(m.group(2)):
                    tot += 1
    print("%-56s %3d键 %d文件" % (t.split("/")[-1], tot, len(bs)))
