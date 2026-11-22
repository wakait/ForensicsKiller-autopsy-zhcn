# -*- coding: utf-8 -*-
"""按「英文值」补译标签式/状态式文案（只改当前仍无中文的值）。"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_new as v  # noqa

PACK = Path(__file__).resolve().parent.parent
CJK = re.compile(r"[\u4e00-\u9fff]")
UNI = re.compile(r"\\\\u([0-9a-fA-F]{4})")

MAP = {
    "Comment:": "备注：",
    "Case:": "案件：",
    "Path:": "路径：",
    "Type:": "类型：",
    "Tag:": "标签：",
    "Tags:": "标签：",
    "Examiner:": "检验人：",
    "Name:": "名称：",
    "Script:": "脚本：",
    "Page:": "页码：",
    "Category:": "类别：",
    "Categories:": "类别：",
    "Notes:": "备注：",
    "Timezone:": "时区：",
    "Profile:": "配置：",
    "Header:": "页眉：",
    "Footer:": "页脚：",
    "Show:": "显示：",
    "Result:": "结果：",
    "Untranslated:": "未翻译：",
    "Scales:": "比例尺：",
    "Scale:": "比例尺：",
    "(Default)": "（默认）",
    "Queuing...": "正在排队...",
    "Running...": "正在运行...",
    "Loading...": "正在加载...",
    "loading...": "正在加载...",
    "Notable: {0}": "关注：{0}",
    "{0} Details": "{0} 详情",
    "Started {0}": "已启动 {0}",
    "{0} events": "{0} 个事件",
    "Tags:\\n{0}": "标签：\\n{0}",
    "\\n\\nTags\\n{0}": "\\n\\n标签\\n{0}",
    "{0} (Cancelling...)": "{0}（正在取消...）",
    "\\\\# Files": "文件数",
    "C&ancel": "取消(&C)",
    "Position: {0} [{1}])": "位置：{0} [{1}])",
}
# 文件大小筛选标签（原值以 ": " 开头）
for k in ("upTo16kb", "16kbto100kb", "100kbto1mb", "1mbto50mb", "50mbto200mb",
          "200PlusMb", "500kbto100mb", "100mbto1gb", "1gbto5gb", "5gbto10gb",
          "10PlusGb", "upTo500kb"):
    pass


def esc(s):
    return "".join("\\u%04x" % ord(c) if ord(c) > 127 else c for c in s)


def main():
    rows = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))["bundles"]
    changed = 0
    for rel, info in sorted(rows.items()):
        p = PACK / info["pack"]
        lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
        out = []
        for line in lines:
            s = line.strip()
            if "=" not in s or s.startswith("#"):
                out.append(line)
                continue
            key, val = s.split("=", 1)
            raw = val
            dec = UNI.sub(lambda m: chr(int(m.group(1), 16)), raw)
            # 文件大小标签：": 100KB-1MB" → "：100KB-1MB"
            if KEY_SIZE.search(key) and re.match(r"^: ", dec):
                out.append("%s=%s" % (key, esc("：" + dec[2:])))
                changed += 1
                continue
            if dec in MAP and not CJK.search(dec):
                out.append("%s=%s" % (key, esc(MAP[dec])))
                changed += 1
                continue
            out.append(line)
        p.write_text("\n".join(out), encoding="utf-8")
    print("补译条目:", changed)


KEY_SIZE = re.compile(r"SearchData\.FileSize\.")

if __name__ == "__main__":
    main()
