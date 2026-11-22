# -*- coding: utf-8 -*-
"""构建「完整便携版」发布包：Autopsy 程序本体 + 已配置好的中文包 → .7z

前提：`--root` 指向一个**已装好中文包**的 Autopsy 安装目录
      （可用 scripts/install_pack.py --root <dir> --set-locale 得到）。

产物结构（解压后）：
    autopsy/                 ← 完整程序（含 jre、solr、模块）
    启动.bat / 启动.ps1       ← 首次运行自动清一次菜单缓存，然后启动
    使用说明.txt

用法：
    python scripts/build_full_release.py --root "D:\\kit-ascii\\autopsy" --version R3
    python scripts/build_full_release.py --root "..." --version R3 --dry-run
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PORTABLE = REPO / "release" / "portable"
DIST = REPO / "dist"
SEVENZIP = Path(r"C:\Program Files\7-Zip\7z.exe")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="已打好中文包的 Autopsy 安装目录")
    ap.add_argument("--version", default="R3")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--level", default="5", help="7z 压缩级别 0/1/3/5/7/9")
    args = ap.parse_args()

    root = Path(args.root)
    if not (root / "bin" / "autopsy64.exe").is_file():
        raise SystemExit("不是有效的 Autopsy 目录：%s" % root)
    if not SEVENZIP.is_file():
        raise SystemExit("未找到 7-Zip：%s（请先安装 7-Zip）" % SEVENZIP)
    if not (root / "AppDataFolder" / "autopsy" / "etc" / "autopsy.conf").is_file():
        print("！警告：未找到 autopsy.conf，界面语言可能不是中文")

    conf = root / "AppDataFolder" / "autopsy" / "etc" / "autopsy.conf"
    if conf.is_file() and "-J-Duser.language=zh" not in conf.read_text(encoding="utf-8", errors="replace"):
        print("！警告：autopsy.conf 未设置中文参数，建议先执行 install_pack.py --set-locale")

    DIST.mkdir(exist_ok=True)
    out = DIST / ("Autopsy-4.23.1-zhCN-portable-%s.7z" % args.version)

    # 启动器临时放进安装根目录的**父目录**，使压缩包根层就是 autopsy/ + 启动.bat
    staging = root.parent
    copied = []
    for name in ("启动.bat", "启动.ps1", "使用说明.txt"):
        src = PORTABLE / name
        dst = staging / name
        if src.is_file() and not dst.exists():
            shutil.copy2(src, dst)
            copied.append(dst)
    try:
        cmd = [str(SEVENZIP), "a", "-t7z", "-mx=" + args.level, "-mmt=on", "-sccUTF-8",
               str(out), str(root.name)] + [p.name for p in copied]
        print("执行：", " ".join(cmd))
        if args.dry_run:
            print("[dry-run] 未实际压缩")
            return
        subprocess.run(cmd, check=True, cwd=str(staging))
    finally:
        for p in copied:
            try:
                p.unlink()
            except OSError:
                pass

    size = out.stat().st_size
    digest = sha256(out)
    (DIST / "SHA256-portable.txt").write_text("%s  %s\n" % (digest, out.name), encoding="utf-8")
    print("\n完成：%s（%.0f MB）" % (out, size / 1048576))
    print("SHA256: %s" % digest)


if __name__ == "__main__":
    main()
