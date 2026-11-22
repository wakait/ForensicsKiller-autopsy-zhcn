# -*- coding: utf-8 -*-
"""补译 Autopsy 侧被「通用标识不强翻」规则漏掉的按钮/列头/状态词。

只改 org/sleuthkit/autopsy/** 下、当前值仍为英文且命中映射表的条目。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_new as v  # noqa

PACK = Path(__file__).resolve().parent.parent
CJK = re.compile(r"[\u4e00-\u9fff]")
UNI = re.compile(r"\\u([0-9a-fA-F]{4})")

MAP = {
    "OK": "确定", "&OK": "确定(&O)", "Ok": "确定",
    "Cancel": "取消", "Canceled": "已取消",
    "Browse": "浏览", "Configure": "配置", "Directory": "目录",
    "Name": "名称", "Type": "类型", "Category": "类别",
    "Value": "值", "Values": "值", "Accounts": "账户",
    "Summary": "摘要", "Description": "描述", "Status": "状态",
    "Item": "项", "Conclusion": "结论", "Configuration": "配置",
    "Justification": "依据", "Score": "得分", "Usage": "用途",
    "Source": "来源", "Message": "消息", "From": "发件人", "To": "收件人",
    "Context": "上下文", "Login": "登录", "Confidence": "置信度",
    "Scope": "范围", "Title": "标题", "Strings": "字符串", "Page": "页码",
    "Favorites": "收藏夹", "Bank": "银行", "Brand": "品牌", "File": "文件",
    "Height": "高度", "Width": "宽度", "None": "无", "none": "无",
    "Priority": "优先级", "Attribute": "属性", "Details": "详细信息",
    "Success": "成功", "Error": "错误", "Refresh": "刷新", "Select": "选择",
    "select": "选择", "Collapse": "折叠", "Expand": "展开",
    "Hide": "隐藏", "Unhide": "显示", "Pin": "固定", "Unpin": "取消固定",
    "Count": "计数", "Apply": "应用", "Reset": "重置", "Save": "保存",
    "Skip": "跳过", "Overwrite": "覆盖", "Zoom": "缩放",
    "Short": "简短", "Medium": "中等", "Full": "完整",
    "Ascending": "升序", "Descending": "降序", "Complete": "完成",
    "Known": "已知", "Path": "路径", "Tags": "标签", "Annotations": "批注",
    "Email": "电子邮件", "Administrator": "管理员", "Address": "地址",
    "Copy": "复制", "Text": "文本", "Ingest": "摄取", "Metadata": "元数据",
    "Test": "测试", "all": "全部", "only": "仅", "others": "其他",
    "Linear": "线性", "Logarithmic": "对数", "End": "结束", "Start": "开始",
    "hours": "小时", "microseconds": "微秒", "milliseconds": "毫秒",
    "minutes": "分钟", "nanoseconds": "纳秒", "seconds": "秒",
    "Analyzed": "已分析", "Hashset": "哈希集", "Regrouping": "重新分组",
    "NewEmptyProfile": "新建空配置", "Main": "主", "Messages": "消息",
    "Calls": "通话", "Icon": "图标", "Translation": "翻译",
    "Options": "选项", "Evidence": "证据", "Case": "案件",
    "Comment": "备注", "Device": "设备", "Continue": "继续",
    "of": "/", "Hash": "哈希",
}


def esc(s):
    return "".join("\\u%04x" % ord(c) if ord(c) > 127 else c for c in s)


def main():
    rows = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))["bundles"]
    changed = 0
    touched = set()
    for rel, info in sorted(rows.items()):
        if not rel.startswith("org/sleuthkit/autopsy"):
            continue
        p = PACK / info["pack"]
        lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
        out, hit = [], 0
        for line in lines:
            s = line.strip()
            if "=" not in s or s.startswith("#"):
                out.append(line)
                continue
            key, val = s.split("=", 1)
            t = UNI.sub(lambda m: chr(int(m.group(1), 16)), val).strip()
            if t in MAP and not CJK.search(t):
                out.append("%s=%s" % (key, esc(MAP[t])))
                hit += 1
            else:
                out.append(line)
        if hit:
            p.write_text("\n".join(out), encoding="utf-8")
            changed += hit
            touched.add(rel)
    print("补译条目:", changed, "涉及 bundle:", len(touched))


if __name__ == "__main__":
    main()
