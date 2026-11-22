# -*- coding: utf-8 -*-
"""全量扫描 Autopsy 安装目录：找出所有含 Bundle.properties 的 jar 与内部路径，
并与已翻译清单（locales/ 下已有的 Bundle_zh_CN.properties）做差集。
只读，不修改任何 jar。
"""
import json
import os
import sys
import zipfile

ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
PACK = r"E:\Snow\Desktop\workspace\2026\取证\决赛备战\autopsy-zhCN-v2026.12-FINAL"
LOCALES = os.path.join(PACK, "locales")


def covered_set():
    """locales/ 下已存在的 bundle 路径（去掉 _zh_CN 后缀）"""
    got = set()
    for dirpath, _, files in os.walk(LOCALES):
        for f in files:
            if f.endswith("_zh_CN.properties"):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, LOCALES).replace("\\", "/")
                got.add(rel.replace("_zh_CN.properties", ".properties"))
    return got


def scan():
    covered = covered_set()
    rows = []
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if not f.endswith(".jar"):
                continue
            jp = os.path.join(dirpath, f)
            reljar = os.path.relpath(jp, ROOT).replace("\\", "/")
            try:
                zf = zipfile.ZipFile(jp)
            except Exception as e:
                rows.append({"jar": reljar, "error": str(e)})
                continue
            names = zf.namelist()
            bundles = [n for n in names if n.endswith("Bundle.properties")
                       and not n.endswith("_zh_CN.properties")]
            if not bundles:
                zf.close()
                continue
            for b in bundles:
                raw = b[:-len("Bundle.properties")] + "Bundle.properties"
                rows.append({
                    "jar": reljar,
                    "bundle": raw,
                    "covered": raw in covered,
                    "size": zf.getinfo(b).file_size,
                })
            zf.close()
    return rows


if __name__ == "__main__":
    rows = scan()
    err = [r for r in rows if "error" in r]
    ok = [r for r in rows if "bundle" in r]
    miss = [r for r in ok if not r["covered"]]
    print("jar 总数(含bundle):", len(set(r["jar"] for r in ok)))
    print("bundle 总数:", len(ok))
    print("已覆盖:", len(ok) - len(miss))
    print("未覆盖:", len(miss))
    if err:
        print("读取失败 jar:", len(err))
    out = os.path.join(PACK, "QA_ALL_MODULES.json")
    json.dump({"total": len(ok), "missing": len(miss), "rows": rows},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("写出:", out)
    print("\n=== 未覆盖模块（按 jar 分组，前 80）===")
    byjar = {}
    for r in miss:
        byjar.setdefault(r["jar"], []).append(r["bundle"])
    for i, (j, bs) in enumerate(sorted(byjar.items(), key=lambda kv: -len(kv[1]))):
        if i >= 80:
            print("... 还有", len(byjar) - 80, "个 jar")
            break
        print("%-62s %d" % (j, len(bs)))
