# Autopsy 简体中文语言包（资源补丁版）

> **直接下载安装包**：[Releases · v2026.12-FINAL-R3](https://github.com/wakait/ForensicsKiller-autopsy-zhcn/releases/latest)（约 0.3 MB，免 Python，双击安装）


面向 **Autopsy 4.23.1**（Sleuth Kit Labs）的独立汉化仓库：不改官方安装包、不重编译，只往 jar 里补资源文件，可一键安装、一键回滚。

- 覆盖 **180 个 bundle、约 8900 个中文条目**：Autopsy 主界面 + Sleuth Kit 数据模型 + NetBeans 平台层 + Cyber Triage 插件
- 菜单栏、常用按钮、对话框、结果表列头、时间线、报告、关键词搜索均已中文化
- 已完成 8 次实机启动验证，0 SEVERE / 0 资源缺失

## 0. 开箱即用（推荐给普通用户）

不想折腾命令行？直接下载发布包：

```
Autopsy-4.23.1-zhCN-<版本>.zip      ≈ 0.3 MB
```

1. 完全退出 Autopsy
2. 解压 → 双击 **安装.bat**
3. 启动 Autopsy，界面即为中文（首次启动重建缓存约 60–90 秒）

不需要装 Python，Windows 自带的脚本引擎即可运行。卸载双击 **卸载.bat** 即可完整还原。
发布包的构建方式见 [`RELEASE.md`](RELEASE.md)。

---

## 1. 效果

| 位置 | 汉化前 | 汉化后 |
|---|---|---|
| 菜单栏 | `Case  View  Tools  Window  Help` | `案件  视图(V)  工具(T)  窗口(W)  帮助(H)` |
| 工具栏 | `Add Data Source` | `添加数据源` |
| 对话框按钮 | `OK / Cancel` | `确定 / 取消` |
| 数据工件树 | `Web Bookmarks / Installed Programs` | `网页书签 / 已安装程序` |
| 结果表列头 | `Name / Type / Path` | `名称 / 类型 / 路径` |

---

## 2. 快速开始（三步）

### 前置

- Windows，Autopsy **4.23.1**（其他版本未验证，不要直接套用）
- Python 3.9+（仅脚本需要，Autopsy 本身不带）

### 第 1 步：确认 Autopsy 完全退出

任务管理器里不应有 `autopsy64.exe`，也不要有残留的 `java.exe`（内置 Solr）。

### 第 2 步：安装

```bat
python scripts\install_pack.py --root "D:\kit-ascii\autopsy" --set-locale
```

- `--root`：Autopsy 安装目录（含 `bin\autopsy64.exe` 的那一层）
- `--set-locale`：同时把 `-J-Duser.language=zh -J-Duser.country=CN` 写进 `autopsy.conf`
- 想先看会改哪些文件：加 `--dry-run`

脚本会：备份原 jar → 写入 `Bundle_zh_CN.properties` → 记录 `INSTALL_LOG.json` → **自动清理 NetBeans layer 缓存**。

### 第 3 步：启动

正常双击 `bin\autopsy64.exe`。**首次启动会重建缓存，约 60–90 秒**，之后正常。

> ⚠️ **最关键的一条**：如果只替换 jar 不清缓存，菜单不会变中文。原因见 [`docs/原理与排错.md`](docs/原理与排错.md)。脚本已自动处理，手工安装时必须删 `%LOCALAPPDATA%\autopsy\Cache\dev\*`。

---

## 3. 校验与回滚

```bat
:: 结构校验（键集合、占位符、转义）
python scripts\verify_new.py

:: 从 jar 内逐个真实加载（需要安装后的目录）
python scripts\loadtest_all.py

:: 回滚（按 INSTALL_LOG.json 的备份还原）
python scripts\rollback_pack.py --yes
```

回滚前会逐个校验备份的 SHA256，与安装前记录不一致就拒绝覆盖。

---

## 4. 多套 Autopsy 安装

机器上有两份以上 Autopsy 时，用这个脚本一次装到指定目录（含清缓存）：

```bat
python scripts\apply_to_root.py --root "D:\TaskSpaces\ToolsKit\tools\autopsy"
```

> 多份安装**共用**同一个用户目录（`%APPDATA%\autopsy`）和缓存（`%LOCALAPPDATA%\autopsy\Cache`）。
> 切换安装后必须再清一次缓存，否则会看到上一个安装的菜单。

---

## 5. 仓库结构

```
autopsy-zhcn/
├─ locales/           # 中文资源：180 个 Bundle_zh_CN.properties（真正的交付物）
├─ templates/         # 对应的英文原文副本（对照、重建用，勿手改）
├─ MANIFEST.json      # 清单：每个 bundle 的 jar、键数、中文数、资源路径
├─ VERSION.md         # 版本记录 + 全部验收过程（含踩坑与结论）
├─ scripts/
│  ├─ install_pack.py        # 安装
│  ├─ rollback_pack.py       # 回滚
│  ├─ apply_to_root.py       # 多安装部署
│  ├─ verify_new.py          # 结构校验
│  ├─ loadtest_all.py        # jar 内实加载回归
│  ├─ patch_layer_names.py   # 菜单 displayName 补丁（菜单不生效时用）
│  ├─ repair_orphans.py      # 清理残留英文续行
│  ├─ fix_buttons.py         # 按钮/列头补译
│  ├─ report_remaining.py    # 盘点剩余英文
│  └─ legacy/                # 历史脚本（构建前期使用，仅备查）
├─ translations/      # 各批译文 JSON 源（可复现，便于增量翻译）
├─ tools/             # 诊断小工具（LoadCheck.java、截图工具）
└─ docs/              # 原理与排错、术语表、验收摘要
```

---

## 6. 翻译约定（术语）

| 英文 | 中文 | 说明 |
|---|---|---|
| Case | 案件 | |
| Data Source | 数据源 | |
| Ingest / Ingest Module | 摄取 / 摄取模块 | 不要用「导入」（import 才是导入） |
| Artifact | **制品** | 含 `Data Artifacts = 数据制品`；禁用「工件 / 产物」 |
| Examiner | 检验员 | |
| Keyword Search | 关键词搜索 | |
| Timeline | 时间线 | |
| Hash Set / Hash Database | 哈希集 / 哈希数据库 | |
| Known Bad / Known Good | 已知恶意 / 已知正常 | |
| Tag / Bookmark | 标签 / 书签 | |

**不翻译**：NetBeans、Java、PostgreSQL、ICEpdf、Cyber Triage、Helvetica 等产品名与字体名；MD5/SHA-1 等算法名；URL、路径、快捷键串。

详细见 [`docs/术语表.md`](docs/术语表.md)。

---

## 7. 常见问题

**Q：装完菜单还是英文？**
99% 是 layer 缓存没清。关闭 Autopsy，删除 `%LOCALAPPDATA%\autopsy\Cache\dev\*`，再启动。脚本已自动做，手工装的话务必手动删。

**Q：菜单中文了，但个别子项仍是英文？**
那是写死在 class 里的字符串（日志/异常文本为主，约 181 条），语言包改不到，需要改字节码，本版未做。

**Q：启动失败 / 界面异常？**
立即回滚：`python scripts\rollback_pack.py --yes`，再清一次缓存。

**Q：Autopsy 升级到新版本还能用吗？**
不能直接用。jar 结构、bundle 路径都可能变，需按 `VERSION.md` 的流程重新导出、翻译、校验。

**Q：会影响取证结果吗？**
只改界面文案资源，不动任何分析逻辑。数值型结论仍以原始数据为准，中文界面只提升操作效率。

---

## 8. 维护：怎么继续补翻译

```bat
:: 1. 盘点还有多少英文没译
python scripts\report_remaining.py

:: 2. 从 jar 导出待译键（示例：按批）
python scripts\export_batch5.py

:: 3. 翻译成 JSON 后落盘（自动写 locales/ 并登记 MANIFEST）
python scripts\add_bundle.py translations\batch5\zh_xxx.json

:: 4. 校验 → 统计 → 安装
python scripts\verify_new.py
python scripts\recount_manifest.py
python scripts\install_pack.py --root "<安装目录>"
```

新增/修改菜单名时，除了 bundle 还要注意 NetBeans 的两种机制，详见 [`docs/原理与排错.md`](docs/原理与排错.md)。

---

## 9. 已知限制

- 仅适配 **Autopsy 4.23.1**；其他版本未验证。
- 约 **181 条**硬编码英文字符串（主要是日志与异常信息）无法通过资源文件汉化。
- 73 条按规范**刻意保留英文**（格式模板、字体名、产品名、Linux 发行版名）。
- 语言包不改变任何分析结果，仅影响界面显示。

---

## 10. 许可与边界

- 本仓库只包含**翻译资源与工具脚本**，不包含 Autopsy 任何代码或二进制文件。
- Autopsy 版权归 Sleuth Kit Labs（Apache License 2.0 / CPL）；使用本语言包前请自行确认符合其许可。
- 安装脚本只写入 `Bundle_zh_CN.properties` 与菜单显示名，改动前均自动备份，可完整回滚。

版本与验收记录见 [`VERSION.md`](VERSION.md)。
