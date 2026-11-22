# -*- coding: utf-8 -*-
"""校验新加入的 bundle（TSK / 平台 / Cyber Triage）：
  1. 键集合与模板一致
  2. MessageFormat/printf 占位符多重集一致
  3. 无双重转义 \\\\uXXXX、无裸 UTF-8 非 ASCII、无非法续行
  4. 统计中文化行数
只校验 MANIFEST 中 jar 不属于 org-sleuthkit-autopsy-* 历史 125 个的新条目？
不——校验全部 156 个，但对新条目用键集合口径、旧条目沿用原校验器。
用法：python scripts/verify_new.py
"""
import json
import re
from collections import Counter
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))
PLACEHOLDER = re.compile(r"\{\d+\}|%\d*\$?[sd]")
DOUBLE_ESC = re.compile(r"\\\\[uU][0-9a-fA-F]{4}")
UNI = re.compile(r"\\u([0-9a-fA-F]{4})")

LEGACY = "org/sleuthkit/autopsy/"


def _cont(raw):
    n = 0
    for ch in reversed(raw):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


def parse(path: Path):
    """返回 (dict, errors)。按 Java properties 规则合并续行。"""
    kv, errors, buf_key, buf_val, buf_raw = {}, [], None, None, None
    text = path.read_text(encoding="utf-8", errors="replace")
    for lineno, raw in enumerate(text.split("\n"), 1):
        raw = raw.rstrip("\r")
        if buf_key is not None:
            buf_val += "\n" + raw
            buf_raw += "\n" + raw
            if not _cont(raw):
                kv[buf_key] = buf_val
                buf_key = None
            continue
        s = raw.strip()
        if not s or s.startswith("#") or s.startswith("!"):
            continue
        if "=" not in s:
            errors.append("L%d 无等号: %r" % (lineno, raw[:60]))
            continue
        k, v = s.split("=", 1)
        if _cont(raw):
            buf_key, buf_val, buf_raw = k.strip(), v, raw
        else:
            kv[k.strip()] = v
    if buf_key is not None:
        errors.append("文件末尾存在未闭合续行: " + buf_key)
    return kv, errors


def check(rel: str, info: dict):
    tpl = PACK / "templates" / rel
    loc = PACK / info["pack"]
    tv, te = parse(tpl)
    lv, le = parse(loc)
    # 模板自身的畸形行（如原厂 jar 里的 "gest"）不算本包缺陷
    tpl_text = tpl.read_text(encoding="utf-8", errors="replace")
    errs = []
    for e in list(te) + [x for x in le if x not in te]:
        if "无等号" in e:
            frag = e.split(":", 1)[1].strip().strip("'")
            if frag and frag in tpl_text:
                continue
        errs.append(e)
    # 允许 locale 追加模板中没有的键（菜单路径键等），但不允许缺键
    if set(tv) - set(lv):
        miss = sorted(set(tv) - set(lv))[:5]
        errs.append("缺键 %d 例:%s" % (len(set(tv) - set(lv)), miss))
    raw = loc.read_bytes()
    if any(b > 127 for b in raw):
        bad = next(i for i, b in enumerate(raw) if b > 127)
        errs.append("存在裸非 ASCII 字节 @%d" % bad)
    if DOUBLE_ESC.search(loc.read_text(encoding="utf-8", errors="replace")):
        errs.append("存在双转义 \\\\uXXXX")
    ph_bad = 0
    for k, v in lv.items():
        if k not in tv:
            continue
        if Counter(PLACEHOLDER.findall(v)) != Counter(PLACEHOLDER.findall(tv[k])):
            ph_bad += 1
            if ph_bad <= 3:
                errs.append("占位符不符 %s: %r vs %r" % (k, v[:40], tv[k][:40]))
    dec = lambda v: UNI.sub(lambda m: chr(int(m.group(1), 16)), v)
    cjk = sum(1 for v in lv.values()
              if any("\u4e00" <= c <= "\u9fff" for c in dec(v)))
    return {"rel": rel, "keys": len(tv), "cjk": cjk, "errors": errs}


def main():
    rows = [(r, i) for r, i in MANIFEST["bundles"].items()]
    total_k = total_c = fails = 0
    for rel, info in sorted(rows):
        r = check(rel, info)
        total_k += r["keys"]
        total_c += r["cjk"]
        if r["errors"]:
            fails += 1
            print("[FAIL] %s" % rel)
            for e in r["errors"][:6]:
                print("       -", e)
    print("\n校验 %d 个 bundle，%d FAIL" % (len(rows), fails))
    print("键合计 %d，含中文值 %d（%.2f%%）" % (total_k, total_c, 100.0 * total_c / total_k))


if __name__ == "__main__":
    main()
