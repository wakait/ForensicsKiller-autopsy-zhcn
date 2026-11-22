# -*- coding: utf-8 -*-
"""把语言包安装到指定 Autopsy 安装目录（支持多份副本）。

  python scripts/apply_to_root.py --root "D:\\TaskSpaces\\ToolsKit\\tools\\autopsy" [--dry-run]

做三件事：
  1. 按 MANIFEST 的 bundle→jar 映射，写入 locales/ 下的 Bundle_zh_CN.properties；
  2. 给菜单文件夹写 layer displayName（复用 patch_layer_names4 的逻辑）；
  3. 在 autopsy.conf 的 default_options 追加 -J-Duser.language=zh -J-Duser.country=CN。
备份落在 backups/<root 标识>/，可用 --restore 还原该 root。
"""
import json
import os
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACK / "scripts"))
import patch_layer_names as L  # noqa


def clear_nb_cache(dry: bool = False) -> str:
    """删除 NetBeans 的合并 layer 缓存，否则 jar 内 layer 改动不会被读取。"""
    import os
    from pathlib import Path as _P
    cands = [
        _P(os.environ.get("LOCALAPPDATA", "")) / "autopsy" / "Cache" / "dev",
        _P(os.environ.get("LOCALAPPDATA", "")) / "autopsy" / "Cache",
    ]
    removed = []
    for d in cands:
        if not d.is_dir():
            continue
        if dry:
            removed.append(str(d) + "（dry）")
            continue
        for p in d.glob("*"):
            try:
                if p.is_dir():
                    import shutil as _sh
                    _sh.rmtree(p, ignore_errors=True)
                else:
                    p.unlink()
            except OSError:
                pass
        removed.append(str(d))
    return ", ".join(removed) if removed else "未找到缓存目录"


def root_tag(root: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(root))[:60]


def backup_dir(root: Path) -> Path:
    return PACK / "backups" / ("install_" + root_tag(root))


def install_bundles(root: Path, man: dict, dry: bool) -> int:
    by_jar = {}
    for rel, info in man["bundles"].items():
        jar = root / info["jar"]
        pack = PACK / info["pack"]
        if not jar.is_file():
            print("   跳过（无此 jar）:", info["jar"])
            continue
        by_jar.setdefault(jar, {})[rel.replace("Bundle.properties", "Bundle_zh_CN.properties")] = pack

    total = 0
    for jar, adds in sorted(by_jar.items()):
        missing = [p for p in adds.values() if not p.is_file()]
        if missing:
            print("   ！缺少资源:", missing[:2])
            continue
        if dry:
            print("   [dry] %-52s +%d" % (jar.name, len(adds)))
            continue
        b = backup_dir(root) / os.path.relpath(jar, root)
        b.parent.mkdir(parents=True, exist_ok=True)
        if not b.exists():
            shutil.copy2(jar, b)
        tmp = jar.with_suffix(".tmp")
        with zipfile.ZipFile(jar) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename in adds:
                    continue
                zout.writestr(item, zin.read(item.filename))
            for name, src in adds.items():
                zout.writestr(name, src.read_bytes().replace(b"\r\n", b"\n"),
                              compress_type=zipfile.ZIP_DEFLATED)
        for _ in range(10):
            try:
                os.replace(tmp, jar)
                break
            except PermissionError:
                time.sleep(1.5)
        else:
            print("   ！替换失败:", tmp.name)
        total += len(adds)
        print("   %-52s +%d bundle" % (jar.name, len(adds)))
    return total


def patch_layers(root: Path, dry: bool) -> int:
    L.ROOT = root
    L.BAK = backup_dir(root) / "layer"
    total, jobs = 0, []
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".jar"):
                continue
            jp = Path(dirpath) / f
            try:
                z = zipfile.ZipFile(jp)
            except Exception:
                continue
            for layer in L.loaded_layers(z):
                try:
                    raw = z.read(layer)
                except Exception:
                    continue
                data, n = L.rewrite(raw)
                if n:
                    jobs.append((jp, layer, data, n))
                    total += n
    print("   layer displayName 待写:", total)
    if dry:
        return total
    for jp, layer, data, n in jobs:
        b = backup_dir(root) / os.path.relpath(jp, root)
        b.parent.mkdir(parents=True, exist_ok=True)
        if not b.exists():
            shutil.copy2(jp, b)
        tmp = jp.with_suffix(".tmp")
        with zipfile.ZipFile(jp) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                zout.writestr(item, data if item.filename == layer else zin.read(item.filename))
        for _ in range(10):
            try:
                os.replace(tmp, jp)
                break
            except PermissionError:
                time.sleep(1.5)
        else:
            print("   ！替换失败:", tmp.name)
    return total


def patch_conf(root: Path, dry: bool) -> str:
    conf = root / "AppDataFolder" / "autopsy" / "etc" / "autopsy.conf"
    if not conf.is_file():
        return "无 autopsy.conf"
    text = conf.read_text(encoding="utf-8", errors="replace")
    if "-J-Duser.language=zh" in text:
        return "已含中文参数"
    marker = 'default_options="'
    i = text.find(marker)
    if i < 0:
        return "未找到 default_options"
    j = text.find('"', i + len(marker))
    new = text[:j] + " -J-Duser.language=zh -J-Duser.country=CN" + text[j:]
    if not dry:
        b = backup_dir(root) / "autopsy.conf"
        b.parent.mkdir(parents=True, exist_ok=True)
        if not b.exists():
            shutil.copy2(conf, b)
        conf.write_text(new, encoding="utf-8")
    return "已追加中文参数"


def main():
    if "--root" not in sys.argv:
        raise SystemExit("用法: --root <autopsy 安装目录> [--dry-run|--restore]")
    root = Path(sys.argv[sys.argv.index("--root") + 1])
    dry = "--dry-run" in sys.argv
    bak = backup_dir(root)

    if "--restore" in sys.argv:
        n = 0
        for b in bak.rglob("*"):
            if b.is_file() and b.name != "autopsy.conf":
                shutil.copy2(b, root / os.path.relpath(b, bak))
                n += 1
        print("已还原", n, "个文件 ->", root)
        return

    man = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))
    print("[1/3] 注入 bundle:", root)
    n1 = install_bundles(root, man, dry)
    print("[2/3] 写入 layer 菜单名")
    n2 = patch_layers(root, dry)
    print("[3/3] autopsy.conf")
    msg = patch_conf(root, dry)
    print("[4/4] 清理 NetBeans layer 缓存:", clear_nb_cache(dry))
    print("\n完成：bundle %d，layer %d 处，conf %s%s"
          % (n1, n2, msg, "（dry-run）" if dry else ""))


if __name__ == "__main__":
    main()
