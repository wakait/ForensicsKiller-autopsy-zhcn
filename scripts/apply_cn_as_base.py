# -*- coding: utf-8 -*-
"""兜底方案：把 jar 内的英文原文 Bundle.properties 直接改写为中文。

理由：`Bundle_zh_CN.properties` 在部分平台模块上未被采用（实测 UI 仍英文），
而 base bundle 一定会被读取。改写 base 不依赖 locale 解析，效果确定。

* 保留原注释与键顺序；值统一写成 \\uXXXX（ASCII 安全，NetBeans 以 ISO-8859-1 读取）
* 原文备份在 backups/base_rewrite/<root标识>/
* 用法：python scripts/apply_cn_as_base.py --root "<安装目录>" [--dry-run|--restore]
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
PACK_ENTRIES = PACK / "locales"


def esc(s: str) -> str:
    return "".join("\\u%04x" % ord(c) if ord(c) > 127 else c for c in s)


def tag(root: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(root))[:60]


def bdir(root: Path) -> Path:
    return PACK / "backups" / "base_rewrite" / tag(root)


def cont(raw: str) -> bool:
    n = 0
    for ch in reversed(raw):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


def rewrite_base(text: str, zh: dict) -> tuple[str, int]:
    """按逻辑行替换值；未收录的键原样保留，新键追加到末尾。"""
    lines = text.split("\n")
    out, seen, i = [], set(), 0
    changed = 0
    while i < len(lines):
        raw = lines[i].rstrip("\r")
        s = raw.strip()
        if not s or s.startswith("#") or s.startswith("!"):
            out.append(raw)
            i += 1
            continue
        block = [raw]
        while cont(lines[i].rstrip("\r")) and i + 1 < len(lines):
            i += 1
            block.append(lines[i].rstrip("\r"))
        i += 1
        if "=" not in block[0]:
            out.extend(block)
            continue
        key = block[0].split("=", 1)[0].strip()
        seen.add(key)
        if key in zh:
            out.append("%s=%s" % (key, esc(zh[key])))
            changed += 1
        else:
            out.extend(block)
    extra = [k for k in zh if k not in seen]
    for k in extra:
        out.append("%s=%s" % (k, esc(zh[k])))
        changed += 1
    return "\n".join(out), changed


def main():
    if "--root" not in sys.argv:
        raise SystemExit("用法: --root <安装目录> [--dry-run|--restore]")
    root = Path(sys.argv[sys.argv.index("--root") + 1])
    dry = "--dry-run" in sys.argv
    bak = bdir(root)

    if "--restore" in sys.argv:
        n = 0
        for b in bak.rglob("*.jar"):
            shutil.copy2(b, root / os.path.relpath(b, bak))
            n += 1
        print("已还原", n, "个 jar")
        return

    man = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))
    per_jar = {}
    for rel, info in man["bundles"].items():
        loc = PACK / info["pack"]
        if not loc.is_file():
            continue
        zh = {}
        for line in loc.read_text(encoding="utf-8", errors="replace").split("\n"):
            s = line.strip()
            if "=" not in s or s.startswith("#"):
                continue
            k, v = s.split("=", 1)
            v = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), v)
            zh[k.strip()] = v
        per_jar.setdefault(info["jar"], {})[rel] = zh

    total = 0
    for jar_rel, bundles in sorted(per_jar.items()):
        jp = root / jar_rel
        if not jp.is_file():
            continue
        newdata, changed = {}, 0
        with zipfile.ZipFile(jp) as z:
            for bundle, zh in bundles.items():
                if bundle not in z.namelist():
                    continue
                text = z.read(bundle).decode("iso-8859-1")
                out, n = rewrite_base(text, zh)
                if n:
                    newdata[bundle] = out.encode("iso-8859-1", "replace")
                    changed += n
        if not changed:
            continue
        print("%-52s 改写 %4d 键" % (jp.name, changed))
        total += changed
        if dry:
            continue
        b = bak / os.path.relpath(jp, root)
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
            print("   ！替换失败:", tmp.name)
    print("\n合计改写:", total, "| dry-run" if dry else "| 已写入")


if __name__ == "__main__":
    main()
