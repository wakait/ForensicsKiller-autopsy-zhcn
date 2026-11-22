# -*- coding: utf-8 -*-
"""精确找出「只译首行、续行仍为英文」的多行值。

判定：逻辑值按 \n 切段后，某一段之后出现「不含任何中文且含 >=4 个英文单词」的段落。
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_new as v  # noqa

PACK = Path(__file__).resolve().parent.parent
CJK = re.compile(r"[\u4e00-\u9fff]")
WORD = re.compile(r"[A-Za-z]{3,}")


def dec(s):
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)


def main():
    rows = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))["bundles"]
    bad = []
    for rel, info in sorted(rows.items()):
        kv, _ = v.parse(PACK / info["pack"])
        for k, val in kv.items():
            t = dec(val)
            if not CJK.search(t):
                continue
            segs = t.split("\n")
            if len(segs) < 2:
                continue
            tail = [s for s in segs[1:] if s.strip()]
            en_tail = [s for s in tail if not CJK.search(s) and len(WORD.findall(s)) >= 4]
            if en_tail:
                bad.append({"bundle": rel, "key": k, "segs": len(segs),
                            "en_segs": len(en_tail), "text": t})
    json.dump(bad, open(PACK / "QA_MIXED.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("确认只译首行的多行值:", len(bad))
    for b, n in Counter(x["bundle"] for x in bad).most_common():
        print("  %-58s %d" % (b, n))
    print()
    for x in bad[:10]:
        print("-- %s | %s (%d 段中 %d 段英文)" % (x["bundle"].split("/")[-2], x["key"],
                                                x["segs"], x["en_segs"]))
        print("   首:", x["text"].split("\n")[0][:70])
        print("   尾:", [s for s in x["text"].split("\n")[1:] if s.strip()][-1][:80])


if __name__ == "__main__":
    main()
