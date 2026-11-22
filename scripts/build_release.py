# -*- coding: utf-8 -*-
"""构建「开箱即用」发布包：dist/Autopsy-4.23.1-zhCN-<ver>.zip

产物结构（用户侧）：
    安装.bat / 卸载.bat / install.ps1 / uninstall.ps1
    使用说明.txt / 版本说明.txt
    payload/bundles.json, payload/layers.json, payload/b/*.properties, payload/l/*.xml

要点：
  * 用户端**不需要 Python**，只需 PowerShell（Windows 自带）；
  * 菜单补丁以「原 layer 全文替换」方式下发，并带原始 SHA256 校验，
    目标 layer 与基线不一致时自动跳过，避免误伤其它版本；
  * 原始 layer 取自备份目录（--backup-root），构建一次后 patched 结果留在
    release/patched/ 与 release/layer_index.json，可脱离备份重新打包。

用法：
    python scripts/build_release.py                    # 构建（需要备份目录）
    python scripts/build_release.py --reuse            # 复用 release/patched/
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
REPO = PACK
REL = REPO / "release"
PATCHED = REL / "patched"
INDEX = REL / "layer_index.json"
DIST = REPO / "dist"
ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
DEFAULT_BACKUP = PACK.parent / "autopsy-zhCN-v2026.12-FINAL" / "backups" / "layerpatch_v4"

sys.path.insert(0, str(PACK / "scripts"))
import patch_layer_names as L  # noqa


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def build_layer_payload(backup_root: Path) -> list:
    """从备份里的原始 layer 生成补丁，返回 layers.json 条目。"""
    items = []
    if not backup_root.is_dir():
        print("！备份目录不存在，跳过 layer 构建：", backup_root)
        return items
    for dirpath, _, files in os.walk(backup_root):
        for f in files:
            if not f.endswith(".jar"):
                continue
            bkp = Path(dirpath) / f
            rel = os.path.relpath(bkp, backup_root)
            with zipfile.ZipFile(bkp) as z:
                for layer in L.loaded_layers(z):
                    try:
                        orig = z.read(layer)
                    except KeyError:
                        continue
                    new, n = L.rewrite(orig)
                    if not n:
                        continue
                    name = "%s__%s.xml" % (f[:-4], hashlib.md5(layer.encode()).hexdigest()[:8])
                    (PATCHED / "l").mkdir(parents=True, exist_ok=True)
                    (PATCHED / "l" / name).write_bytes(new)
                    items.append({
                        "jar": rel.replace("/", "\\"),
                        "entry": layer,
                        "file": "l/" + name,
                        "expect": sha(orig),
                        "added": n,
                    })
                    print("   layer 补丁 %-46s %-34s +%d" % (f[:46], layer.split("/")[-1][:34], n))
    return items


def load_layer_index() -> list:
    if not INDEX.is_file():
        return []
    return json.loads(INDEX.read_text(encoding="utf-8"))


def build_bundles() -> list:
    man = json.loads((REPO / "MANIFEST.json").read_text(encoding="utf-8"))
    out_dir = REL / "payload_b"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    items = []
    for i, (rel, info) in enumerate(sorted(man["bundles"].items())):
        src = REPO / info["pack"]
        if not src.is_file():
            print("   缺资源，跳过：", rel)
            continue
        name = "b%03d.properties" % i
        (out_dir / name).write_bytes(src.read_bytes().replace(b"\r\n", b"\n"))
        items.append({
            "jar": info["jar"],
            "entry": rel.replace("Bundle.properties", "Bundle_zh_CN.properties"),
            "file": "b/" + name,
        })
    return items


def collect_layers() -> list:
    out = []
    for it in load_layer_index():
        src = PATCHED / it["file"]
        if not src.is_file():
            print("   缺 layer 载荷，跳过：", it["file"])
            continue
        out.append(it)
    return out


def write_manual(path: Path, man: dict) -> None:
    t = man["totals"]
    text = f"""Autopsy 简体中文语言包  使用说明
=====================================

版本：{man['version']}
适配：Autopsy 4.23.1（Windows）
规模：{t['bundles']} 个资源包、约 {t['translated']} 条中文文案

一、安装（三步）
---------------
1) 完全退出 Autopsy（任务管理器里不要有 autopsy64.exe）
2) 双击「安装.bat」
   · 会自动查找 Autopsy 安装目录
   · 找不到时按提示输入，例如：D:\\kit-ascii\\autopsy
3) 启动 Autopsy 即可看到中文界面
   · 首次启动会重建缓存，约需 60-90 秒，请耐心等待

二、卸载
---------------
双击「卸载.bat」，会从最近一次安装的备份还原，并清理缓存。

三、常见问题
---------------
Q: 装完菜单还是英文？
A: 99% 是缓存没清。关闭 Autopsy，删除
   %LOCALAPPDATA%\\autopsy\\Cache\\dev 下的所有内容，再启动。
   （安装脚本会自动清理，若被安全软件拦截需手动删）

Q: 个别地方仍是英文？
A: 约有 181 条字符串写死在程序代码里（多为日志与异常提示），
   无法通过语言包汉化，属正常现象。

Q: 提示"安装包与本机版本不一致，已跳过"？
A: 说明本机 Autopsy 不是 4.23.1，请勿强行安装。

Q: 想恢复英文？
A: 运行「卸载.bat」。

四、说明
---------------
· 本语言包只修改界面文字，不影响任何取证分析逻辑与结果。
· 安装前会自动备份原始文件，位置：
  %LOCALAPPDATA%\\autopsy-zhcn\\backup-<时间戳>\\
· 不含 Autopsy 任何代码或二进制文件。

详细原理、术语与验收记录见仓库：README.md / docs/
"""
    path.write_text(text, encoding="utf-8-sig")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backup-root", default=str(DEFAULT_BACKUP))
    ap.add_argument("--reuse", action="store_true", help="复用 release/patched 与 layer_index.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    man = json.loads((REPO / "MANIFEST.json").read_text(encoding="utf-8"))
    ver = man["version"].replace("v2026.12-FINAL", "R3") if "R3" not in man["version"] else man["version"]

    print("[1/4] 构建 layer 补丁")
    if args.reuse and INDEX.is_file():
        layers = collect_layers()
        print("   复用已有：%d 条" % len(layers))
    else:
        layers = build_layer_payload(Path(args.backup_root))
        if layers:
            INDEX.write_text(json.dumps(layers, ensure_ascii=False, indent=1), encoding="utf-8")

    print("[2/4] 准备 bundle 资源")
    bundles = build_bundles()
    print("   %d 个 bundle" % len(bundles))

    print("[3/4] 组装 payload")
    payload = REL / "payload"
    if payload.exists():
        shutil.rmtree(payload)
    (payload / "b").mkdir(parents=True)
    (payload / "l").mkdir(parents=True)
    for it in bundles:
        shutil.copy2(REL / "payload_b" / Path(it["file"]).name, payload / it["file"])
    for it in layers:
        shutil.copy2(PATCHED / it["file"], payload / it["file"])
    (payload / "bundles.json").write_text(json.dumps(bundles, ensure_ascii=False), encoding="utf-8")
    (payload / "layers.json").write_text(json.dumps(layers, ensure_ascii=False), encoding="utf-8")

    print("[4/4] 打包 zip")
    DIST.mkdir(exist_ok=True)
    zip_name = "Autopsy-4.23.1-zhCN-%s.zip" % ver
    zip_path = Path(args.out) if args.out else DIST / zip_name
    base = Path(zip_name).stem
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in ["install.ps1", "uninstall.ps1", "安装.bat", "卸载.bat"]:
            z.write(REL / f, "%s/%s" % (base, f))
        man_txt = REL / "_使用说明.txt"
        write_manual(man_txt, man)
        z.write(man_txt, "%s/使用说明.txt" % base)
        for root, _dirs, files in os.walk(payload):
            for f in files:
                p = Path(root) / f
                z.write(p, "%s/payload/%s" % (base, p.relative_to(payload).as_posix()))
        # 版本说明
        z.writestr("%s/版本说明.txt" % base,
                   ("%s\n\n%s\n" % (man["version"], man.get("totals", {}).get("batch6_note", ""))).encode("utf-8-sig"))

    size = zip_path.stat().st_size
    digest = sha(zip_path.read_bytes())
    (DIST / "SHA256.txt").write_text("%s  %s\n" % (digest, zip_path.name), encoding="utf-8")
    print("\n完成：%s（%.1f MB）" % (zip_path, size / 1048576))
    print("SHA256: %s" % digest)
    print("条目：bundle %d、layer %d" % (len(bundles), len(layers)))


if __name__ == "__main__":
    main()
