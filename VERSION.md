# Autopsy 简体中文语言包 — v2026.12-FINAL

> **版本定位**：2026 年底冻结版 / 文档版本（Document Version），作为年底前汉化项目与线下取证使用的唯一基准。
> **当前修订**：`-R3`（2026-11-22 下午：菜单栏与常用按钮补丁；第四批补 TSK 数据模型 / NetBeans 平台层 / Cyber Triage 共 30 bundle；第五批补打印 / 快速搜索 / 多标签 / 模板 / 帮助 / 启动消息共 18 bundle；修复 90 行「只译首行、旧英文续行残留」缺陷；共 173 bundle、9789 键、8572 中文值，可译口径 **≈100%**）
> **基线软件**：Autopsy 4.23.1（Sleuth Kit Labs），JRE 21。
> **生成日期**：2026-11-22　|　**目标冻结**：2026-12-31
> **主工作区**：`E:\Snow\Desktop\workspace\2026\取证\决赛备战\autopsy-zhCN-v2026.12-FINAL\`

---

## 1. 版本身份

| 项 | 值 |
|---|---|
| 语言包版本 | `v2026.12-FINAL` |
| 适配基线 | Autopsy 4.23.1（其他版本**未验证**，禁止直接套用） |
| 交付形态 | 独立资源包 + 安装/回滚脚本 + 模板 + 清单，不改写官方原件 |
| 资源路径 | `locales/org/sleuthkit/autopsy/**/Bundle_zh_CN.properties` |
| 模板路径 | `templates/org/sleuthkit/autopsy/**/Bundle.properties`（来自 `Bundle.properties-MERGED`） |
| 机器清单 | `MANIFEST.json`（逐包 key 数、译出数、来源 jar） |
| 安装记录 | `INSTALL_LOG.json`（安装后生成，含每个 jar 的原始 SHA256 与备份路径） |

**版本规则**：`v2026.12-FINAL` 一旦冻结，只允许修订补丁号（`-R1`、`-R2`），不得改变版本号语义。任何针对新 Autopsy 版本的移植必须新建版本目录。

---

## 2. 为什么需要独立语言包

Autopsy 4.23.1 自身**没有任何中文语言包**。本地安装树 1064 个 jar 中：

- Autopsy 自有 bundle：英文（默认）109 / 阿拉伯语 105 / 日语 105，**中文 0**；
- 仅 7 个 `zh_CN` 资源属于第三方库（icepdf 阅读器、jfreechart、javafx），与 Autopsy 界面无关；
- 界面字符串总量 **8058 条 / 125 个 bundle**（官方翻译要求基于 `Bundle.properties-MERGED`）。

因此不能指望切换系统 locale 得到中文界面；必须生成 `Bundle_zh_CN.properties` 并注入对应模块 jar。

---

## 3. 目录结构

```
autopsy-zhCN-v2026.12-FINAL/
├── VERSION.md                    本文件（版本说明）
├── HANDOFF-开发专家团.md          派发与分工文档
├── MANIFEST.json                 机器清单（覆盖率、来源 jar）
├── templates/                    从官方 jar 提取的 MERGED 英文模板
├── locales/                      中文语言包（按 Java 包路径排列）
├── scripts/
│   ├── build_pack.py             从官方 jar 重新提取模板并重建骨架
│   ├── install_pack.py           备份 + 注入资源（可逆）
│   └── rollback_pack.py          按 SHA256 校验后回滚
└── backups/                      安装时生成，存放原 jar 与 autopsy.conf 备份
```

---

## 4. 使用流程（线下取证现场）

### 4.1 安装（赛前准备机上完成，不要在现场临时做）

```bash
# 1. 先看计划，不写任何文件
python scripts/install_pack.py --dry-run --set-locale

# 2. 实际安装（自动备份原 jar，记录 SHA256）
python scripts/install_pack.py --set-locale

# 3. 重启 Autopsy，界面应为简体中文
```

`--set-locale` 会在 `autopsy.conf` 的 `default_options` 末尾追加
`-J-Duser.language=zh -J-Duser.country=CN`，并备份原文件。若不想改配置，可省略该参数，改为手动在启动时指定 locale。

### 4.2 回滚

```bash
python scripts/rollback_pack.py --dry-run
python scripts/rollback_pack.py --yes
```

回滚会逐个校验备份 SHA256 与安装前记录一致，再覆盖恢复；全部成功后把 `INSTALL_LOG.json` 改名为 `.json.rolled-back`。

### 4.3 现场红线

1. **检材只读**：Autopsy 案件目录与镜像必须放在工作盘，原始检材不得写入；语言包安装与回滚都只动 Autopsy 工具目录。
2. **哈希留痕**：安装前后 jar 的 SHA256 记录在 `INSTALL_LOG.json`，交接时一并归档。
3. **不接云端模型**：Autopsy 4.23.1 内置 MCP Server 为只读、仅本机连接，但**客户端若使用云端 LLM，案件数据会外传**。线下取证只允许本地 LLM 或完全不启用 MCP。
4. **不在线更新**：禁用 Autopsy 自动更新，避免升级覆盖已注入资源。
5. **离线预案**：本语言包为纯资源文件，不依赖网络；但请在无网环境预演一次安装与回滚。

---

## 5. 翻译状态与验收口径

**当前构建结果（2026-11-22）**：125 个 bundle / 8058 条键，已译出 **4810 条，覆盖率 59.69%**（MANIFEST.json 口径）。四批专家团作业（核心界面 / 查看器与数据模型 / 取证模块 / 补充批次）已完成；未译项保留英文，不影响启动与功能。`QA_REPORT.json` 为早期构建快照，最终以逐行结构验收为准：**0 键错位、0 键名污染、0 悬空续行**。已通过 `repair_pack.py` 修复 10 处「值被下一行键名污染」的系统性损坏（涉及 allcasessearch / casemodule / corecomponents / diagnostics×4 / filesearch / timeline / ingest），并修正 keywordsearch 的 8 处过度反斜杠转义；但后续 `build_pack.py` / `repair_pack.py` / `canonicalize_pack.py` / `finalize_pack.py` 的反斜杠处理不可逆地互相叠加，已全部**停用**。最终语言包由 `rebuild_final.py` 以模板逐行方式重建，并人工修复 diagnostics 一处残留；**不要再次运行任何旧构建/修补脚本**，否则会再次破坏转义。

- 覆盖率以 `MANIFEST.json` 的 `totals.coverage_percent` 为唯一口径（QA_REPORT 按唯一键统计，数值会低约 0.1 个百分点）。
- 未翻译的 key 保留英文原值（不会导致资源缺失或界面报错），逐包状态见 MANIFEST。
- 验收标准：**高频操作路径**（新建案件 → 添加数据源 → 摄取模块 → 文件系统浏览 → 制品查看 → 关键词搜索 → 报告导出）的按钮、菜单、状态提示必须有中文；低频描述性文本允许保留英文。
- 每条翻译必须保留 `{0}` / `%s` / HTML 标签 / 快捷键 `&` 等占位符；技术专有名词（EXIF、Hash、NTFS、MAC、SHA-1 等）保留英文。

---

## 6. 已知限制

1. 本包只覆盖 `org/sleuthkit/autopsy/**`；第三方库（icepdf、jfreechart 等）自带语言包不在此版本范围。
2. 只做界面字符串本地化，**不改变任何取证逻辑、解析规则或报告格式**；答题口径仍以原始英文界面/CLI 输出为准。
3. 不同 Autopsy 版本jar 结构与 key 集合会变，跨版本使用需重新执行 `build_pack.py`。
4. 注入资源会改变 jar 的 SHA256；若某 jar 带签名（安装脚本会告警），签名可能失效，需评估后再安装。
5. 翻译完成度取决于专家团推进情况，本文件不承诺 8058 条全部译出。

## 7. 独立验收记录（2026-11-22）

由主理人不复用项目脚本、直接从磁盘逐行读取并交叉验证：

| 检查项 | 方法 | 结果 |
|---|---|---|
| 文件完整性 | 125 bundle，模板行 vs 语言包行 | 8057 行 vs 8057 行，**长度不一致 0** |
| 键顺序 | 逐行 key 对比 | **错位 0** |
| 键名污染（值中混入下一个 key） | 正则扫描 | **0** |
| 悬空续行符（值尾奇数反斜杠） | 逐行扫描 | **0**（模板自带 `\ ` 已核对为原样保留） |
| 双重 `\uXXXX` 转义 | 解码后扫描 | **0** |
| 反斜杠转义层级 | 全量统计 | 最大 2 级（`\n`/`\!`），无 8 级残留 |
| 真实 Java 加载 | Autopsy JRE 21 `Properties.load()` 载入 125 文件 | keys=8065，含中文 4681，**suspicious=0** |

**结论：结构验收与加载验收均正常，v2026.12-FINAL 可作为线下取证用版本。**

口径说明：文本逐行口径为 4810/8057 条被改写（59.69%）；JRE 加载口径因重复键合并与续行合并为 4681/8065 条含中文（58.04%）。两者差异属统计口径，非数据缺失。

## 8. 实机启动与生效验证（2026-11-22）

- **安装**：`install_pack.py --set-locale` 执行成功，125 个 bundle 注入 6 个 jar，SHA256 与备份记于 `INSTALL_LOG.json`。
- **关键坑**：必须从 ASCII 别名 `D://kit-ascii//autopsy//bin` 启动；从 E 盘中文路径启动会弹 Error 且不写日志（与语言包无关）。
- **第二处坑**：实际生效配置是 `tools/autopsy/etc/autopsy.conf`，不是 `AppDataFolder/autopsy/etc/autopsy.conf`；已修正并备份 `backups/autopsy-real.conf.bak`。
- **启动验证**：Autopsy 4.23.1 主窗口正常运行（Responding=True，~984MB），`messages.log` 的 Input arguments 含 `-Duser.language=zh -Duser.country=CN`。
- **ResourceBundle 实加载**：用 Autopsy 自带 JRE 21 从注入后的 jar 加载，`locale=zh_CN`；corecomponents 313 键/247 中文、casemodule 477/436、actions 82/80、keywordsearch 392/363。**汉化已生效**。
- GUI 截图需虚拟桌面授权（需用户输入电脑密码），本次未做；改以 ResourceBundle 程序化加载为证据。

## 9. 第二批汉化与全库修复（2026-11-22 下午，-R1 修订）

### 9.1 第二批新增汉化（20 个 bundle）

| 线 | 承担人 | bundle | 新增中文行 |
|---|---|---|---|
| A | i18n-core | experimental/autoingest、experimental/configuration | 573 |
| B | i18n-extra | logicalimager/configuration、logicalimager/dsp、modules/leappanalyzers | 260 |
| C | i18n-viewers | contentviewers(补)、geolocation、imagegallery(+actions)、centralrepository/contentviewer、datamodel/hosts | 229 |
| D | 主理人接管（原指派 worker 停滞 3.5h 零写入，直接接手完成） | filetypeid、fileextmismatch、embeddedfileextractor、photoreccarver、portablecase、kml、timeline/ui、timeline/actions、centralrepository/datamodel | 436 |

### 9.2 三个全库级缺陷的修复（重要）

1. **`\\n` / `\\t` 双重转义（36 bundle / 152 行）**：骨架生成阶段把换行、制表符写成了双反斜杠，Java 会读成字面文本 `\n` 而非换行。已用 `fix_double_escape.py` 精确折叠（只折叠"恰好 2 个反斜杠 + n/t"，保留合法的单反斜杠续行与 4 级路径转义）。**修复后 JRE 实测真换行数由 0 变为正确值**。
2. **`embeddedfileextractor` 结构缺陷**：原 locale 第 15 行被内联成全文却残留 16-20 续行，导致 JRE 产生垃圾键 `Embedded`（键数异常）。已按模板续行结构重写，修复后 45 键、无垃圾键、长描述 8 个真换行。
3. **`corecomponents` 键名污染（第一批遗留 1 处）**：`DataResultViewerThumbnail.filePathLabel.text` 的值吞掉了下一行 key。已恢复为模板的 3 个转义空格，key 归还并译出。

### 9.3 验收器口径修正（避免误报）

`verify_batch2.py` 修复了三处误报：① 占位符 `{0}/{1}` 顺序改为多重集合比较（MessageFormat 按索引取值，中文按语序重排合法）；② `&` 助记符（`&C→&复`）不计入占位符；③ 续行判断改为"奇数个反斜杠结尾"，`\ `（转义空格）不再被误判为续行。

### 9.4 第二批验收结果

- **结构验收**：全库 125 bundle，`verify_all.py` → **0 FAIL**（行数、key 顺序、重复键、键名污染、双重转义、占位符全部通过）。
- **JRE 实加载**：125 bundle 全部 `locale=zh_CN`、**0 失败**、8064 键、6178 个中文键。
- **从注入后 jar 实加载**：6 jar 完整性 OK，125 个 zh_CN 条目齐全；抽样 filetypeid/embeddedfileextractor/timeline.ui/centralrepository.datamodel/autoingest/contentviewers 均中文正常、换行正确。
- **覆盖率**：**6202/8057 = 76.98%**（第一版 59.69%）。

### 9.5 重注入与实机验证

- 重注入前 Autopsy 未运行；6 个 jar 重新注入成功，`INSTALL_LOG.json` 的 `sha256_before` 已用原始快照修正，`rollback_pack.py --dry-run` 6 jar 备份哈希全部校验通过（回滚可用）。
- Autopsy 从 ASCII 路径 `D://kit-ascii//autopsy//bin` 启动成功，`Responding=True`。日志确认启动参数含 `-Duser.language=zh -Duser.country=CN`，且 **无任何 Bundle 缺失/资源加载错误、无 SEVERE/FATAL**。
- 启动方式坑：用普通 `Start-Process` 启动，进程会随父 console 关闭而终止；改用 `explorer.exe "…\autopsy64.exe"` 可让 Autopsy 完全脱离 shell 进程树存活。
- GUI 截图仍需虚拟桌面授权，本次以「运行中进程 + 零资源错误日志 + jar 内 ResourceBundle 实加载」作为生效证据链。

---

## 10. 第三批汉化（-R2，2026-11-22 下午）

### 10.1 为什么要先重算分母

第二批结束后，行口径覆盖率 76.98%，看似还有 23%（约 1855 行）未译。逐条核查后发现，其中大量是**不可译 token**：设计期占位符（`text=` 空值）、纯数字与格式串（`{0} / {1}`、`00:00`）、快捷键单字母（`C` / `O` / `F`）、字体名（`Helvetica`、`Courier-Bold`）、产品与库名（`ICEpdf Viewer RI`、`SHA1`）、文件路径（`C:/Program Files/HxD/HxD.exe`）、URL。

因此新增 `scripts/audit_translatable.py`：只有"像人话"的值（≥3 字母单词 + ≥2 个词块或句末标点）才计入可译分母，并排除上述类别。重算后的真实缺口为 **844 行 / 121 bundle**，而非 1855 行。

### 10.2 新增工具链（本轮固化）

| 脚本 | 作用 |
|---|---|
| `scripts/audit_translatable.py` | 审计**可译**覆盖率；`--list` 列未译项（含多行标记）；接 CLI 传 bundle 名 |
| `scripts/list_todo.py` | 按 bundle 列待译键、行号、多行标记（含续行真实英文） |
| `scripts/apply_translations.py` | 按 `{key: 中文}` 映射批量回写，**只改第一个 `=` 之后的值**，多行值自动跳过，保持行数与 key 顺序不变 |
| `scripts/escape_all.py` | 整行非 ASCII → `\uXXXX`（覆盖续行内中文，`escape_values.py` 只处理含 `=` 的行，不够用） |

流程固定为：**写映射 JSON → apply_translations.py → escape_all.py → verify_batch2.py**。全程不解析 Java Properties 语义，避免第二批的续行合并事故重演。

### 10.3 第三批成果

- 覆盖 **49 个 bundle、约 743 行**：thunderbirdparser、modules/dataSourceIntegrity、modules/plaso、healthmonitor、casemodule/services、experimental/volatilityDSP、url/analytics/domaincategorization、centralrepository/ingestmodule、modules/yara(/ui)、timeline/ui/detailview·countsview·listvew、timeline/datamodel/eventtype、report/modules/html·excel·caseuco·taggedhashes·bodyfile·file、livetriage、imagegallery/gui(/drawableviews·navpanel)、contentviewers/(annotations·contextviewer·textcontentviewer·osaccount·analysisresults)、events、rejview、mcp、texttranslation(/ui·translators)、datamodel/(accounts·persons)、datasourceprocessors(/xry)、menuactions、modules/(encryptiondetection·vmextractor·drones·pictureanalyzer)、guiutils、python、timeline/(zooming·explorernodes·ui/filtering)、centralrepository(/eventlisteners·application)、report、examples、imagewriter、machinesettings、textextractors、datasourcesummary/(uiutils·datamodel)、communications、corecomponentinterfaces、directorytree/actionhelpers、geolocation/datamodel、ingest/runIngestModuleWizard、recentactivity(-windows)、modules/embeddedfileextractor、keywordsearch/infastructure 等。

- **刻意保留英文 27 行**：Linux 发行版名（`Linux（Debian）` 等 13 条）、Cookie 进度标签（`Microsoft Edge Cookies` 等 4 条）、产品/库名（`ICEpdf Viewer RI`、`Google Earth KML`、`OpenCV FFMpeg`）、路径（`C:/Program Files/HxD/HxD.exe`）、关键字串（`mcp ai claude llm server`）、`GMT / UTC`。这些属于专有名词或技术标识，译出反而不利于对照。

### 10.4 验收（全部通过）

- **结构**：`verify_all.py` 全库 125 bundle → **0 FAIL**（行数、key 顺序、重复键、键名污染、双重转义、占位符）。
- **目录实加载**：`locales` 直接加载 125/125 成功、0 失败、8064 键、**7004 个中文键**（第二批为 6178）。
- **注入后 jar 实加载**：抽样 16 个新译 bundle 全部 `locale=zh_CN`、0 失败、329 中文键；`embeddedfileextractor` 长描述仍为 8 个真换行。
- **覆盖率**：行口径 **7028/8057 = 87.23%**；**可译口径 5581/5608 = 99.5%**。

### 10.5 重注入与实机

- Autopsy 未运行时重新注入 6 个 jar（core 109 / experimental 4 / imagegallery 7 / keywordsearch 2 / recentactivity 2 / thunderbirdparser 1 = 125 bundle），zip 完整性 OK。
- `INSTALL_LOG.json` 的 `sha256_before` 再次用原始快照回填，`rollback_pack.py --dry-run` 6 jar 备份哈希全部校验通过（回滚可用）。
- 从 `D:/kit-ascii/autopsy/bin` 启动成功（`explorer.exe` 方式脱离 shell 进程树），`Responding=True`、969MB。
- 日志确认 `-Duser.language=zh -Duser.country=CN` 已入参，**无 Bundle 缺失、无资源加载错误、无 SEVERE/FATAL**。

---

## 11. 第四、五批：把「功能里的英文」补完（-R3，2026-11-22 傍晚）

### 11.1 起因与诊断

第三批后仍有人反馈「某些功能里还是英文」。逐 jar 全量扫描（`scripts/scan_all_modules.py`）发现：安装树共 **349 个 Bundle.properties**，而语言包只覆盖 **125 个**。缺的不是 Autopsy 自己的包，而是三层：

| 层 | 说明 | 影响面 |
|---|---|---|
| Sleuth Kit 数据模型 | `org/sleuthkit/datamodel/Bundle.properties`（462 键） | 「数据工件」树的类型名、结果表列头、时间线事件名、数据库连接报错 |
| NetBeans 平台层 | dialogs / explorer / core-windows / output2 / uihandler / options-api / print / quicksearch 等 | 全平台对话框的「确定/取消」、窗口菜单、输出窗口、异常报告、打印、快速搜索 |
| Cyber Triage 插件 | `com/basistech/df/cybertriage/autopsy/**`（5 包 127 键） | 选项面板里的恶意软件扫描、许可证对话框 |

同时排除两个误判：ICEpdf（PDF 阅读器）与 jfreechart **自带 `MessageBundle_zh_CN.properties`**，不是缺口。

### 11.2 加载方式核实（决定能否生效）

- TSK：`BundleProvider` 调用单参 `ResourceBundle.getBundle("org.sleuthkit.datamodel.Bundle")` → 跟随默认 Locale，放 `Bundle_zh_CN.properties` 即生效。
- NetBeans：`NbBundle` 走标准 ResourceBundle 候选链，`Bundle_zh_CN.properties` 优先级高于 `Bundle.properties`。
- 全部目标 jar **未签名**（`META-INF/*.SF` 为空），增补资源不会破坏模块校验。

### 11.3 本批新增资源（48 个 bundle）

- **TSK 数据模型 1 包 462 键**：工件名（常规信息/网页书签/网页 Cookie/网页历史/已安装程序/USB 设备接入…）、属性列名（日期/时间、名称、值、标志、路径…）、时间线事件类型、筛选器名、枚举标签、`DatabaseConnectionCheck` 连接报错。
- **平台层 29 包 811 键**：`org.openide`（OK/Cancel/Close）、explorer 属性表与树视图、core-windows（窗口动作/选项/服务/工具栏）、output2（输出窗口）、uihandler+exceptions（异常报告）、options-api（选项框架/导出）、print（打印/页面设置）、quicksearch、core-multitabs、javahelp、templates、sendopts、core startup。
- **Cyber Triage 5 包 127 键**：扫描器选项、许可证、事件导入、云端配额提示。

### 11.4 同时修复的「半汉化」缺陷（重要）

第三批曾把多行值折叠成单行中文，但**没有删除原来的英文续行**。这些行不含 `=`，Java 会把它们当成「空值键」，结果是：值本身是中文，但文件里残留 90 行英文垃圾键，且人工核对时容易误判为「没翻译」。

- 修复脚本：`scripts/repair_orphans.py`（只删「无 `=`、且不属于奇数反斜杠续行」的行）。
- 保留一个原厂自带的畸形行（`ingest/Bundle.properties` 第 155 行 `gest` 与重复键），以保持与基线逐行可比；校验器把它列为「模板既有」，不计为本包缺陷。
- 另补齐 71 条被「单值不译」口径漏掉的真实文案：`Message`/`Cancelling...`/`Summary`/`Root`/`Other`、`Comment:`/`Case:`/`Examiner:`/`Tags:`/`Timezone:` 等标签，以及 `Loading...`/`Queuing...`/`Running...` 等状态词。

### 11.5 验收（-R3）

| 项目 | 结果 |
|---|---|
| 结构校验 `verify_new.py` | **173 bundle / 0 FAIL**（键集合、占位符多重集、双重转义、裸 UTF-8） |
| 全量实加载 `loadtest_all.py` | **173/173 通过**，9789 键、**8572 个中文值**、0 MISS、0 WARN |
| jar 完整性 | 20 个 jar `testzip()` 全通过，共 173 个 `Bundle_zh_CN.properties` |
| 回滚 | `rollback_pack.py --dry-run` 20/20 备份哈希校验通过 |
| 实机启动 | Autopsy 从 `D:/kit-ascii/autopsy/bin` 启动，PID 44728、Responding、**0 SEVERE/FATAL、无 Bundle 缺失**，并自动打开 case2 |
| 剩余英文 | 77 条，均为格式模板（`{0} / {1}`）、日志器名、字体名（Helvetica/Courier）、产品名（ICEpdf、Cyber Triage、Google Earth KML）、系统发行版名 —— 按既定口径不译 |

### 11.6 仍然无法用语言包解决的部分

`scripts/scan_hardcoded.py` 扫出 Autopsy 四个主 jar 中约 **1808 条硬编码英文字符串**；进一步筛「同时引用 JOptionPane/DialogDescriptor 的类」后为 **181 条**，绝大多数是日志与异常文本（如 `Error indexing content`），少量可能进入对话框。这类字符串写死在 class 常量池里，只能改字节码，风险高、收益低，**未做改动**，如实记录。

---

## 12. 菜单栏与常用按钮（-R3 补丁，2026-11-22 15:45）

### 12.1 为什么前几批没修到菜单

两条独立原因，之前都被漏掉：

1. **主菜单栏的显示名来自一个我们从未覆盖的包**：`org/netbeans/core/ui/resources/Bundle.properties`（`org-netbeans-core-ui.jar`）。它用**路径键**给菜单命名：`Menu/File`、`Menu/Edit`、`Menu/View`、`Menu/Tools`、`Menu/Help`、`Menu/Window/Web`、`Menu/Window/Tools`，还有 `UI/Services`（选项）、`Toolbars/*`。这个包不在前 173 个 bundle 里，所以「视图/工具/帮助/窗口」永远是英文。
2. **常用按钮被旧规则挡掉**：第二批的作业规范写了「通用标识不强翻：Default、OK、Cancel 保留原样」。结果 `OK`（29 处）、`Cancel`（21 处）、`Browse`、`Configure`、`Save`、`Apply`、`Reset`、列头 `Name/Type/Path` 全部留英文。

### 12.2 本轮改动

| 内容 | 数量 |
|---|---|
| 新增/补译 bundle | 7（core-ui resources、favorites、javahelp resources、print resources、core、core/actions、core/ui） |
| 补译按钮/列头/状态词 | 203 条（53 个 bundle）＋ 9 条（Default/Unknown/On/LOCAL） |
| 菜单路径键 | 27 条（Menu/*、Actions/*、Toolbars/*、UI/Services） |
| 菜单子项补充键 | `Menu/Help`、`Actions/Help`（javahelp）、`QuickSearch/Help|GoToOption|Recent` |
| 核心提示 | 115 条（Unexpected Exception、Save All、快捷键编辑器等） |

### 12.3 关键机制（后续维护必读）

- NetBeans 的**文件夹显示名 = 在 `SystemFileSystem.localizingBundle` 指定的包里查「文件夹路径」键**；查不到就直接显示文件夹名（英文）。
- 因此新增菜单/子菜单时，必须在对应 bundle 里补**路径键**，只给动作类加名字是不够的。
- 工具：`scripts/scan_layer_paths.py` 会遍历所有 jar 的 `layer.xml`，列出「有 localizingBundle 但缺路径键」的文件夹。当前 44 个里已译 29，其余 15 个属于 jshell-snippets、FlatLaf 配色、Keymaps 编辑器等**正常界面不可见**的节点。
- `add_bundle.py` 会按模板重建文件；**重建多 bundle 共用文件时必须用 `scripts/merge_rebuild.py` 合并历史映射**，否则会把旧译文冲掉（本轮误伤过 uihandler/options/javahelp，已修复）。

### 12.4 验收

- `verify_new.py`：**180 bundle / 0 FAIL**
- `loadtest_all.py`：**180/180**，9976 键、**8919 中文值**，0 MISS/0 WARN
- 菜单资源 jar 内实加载：`org.netbeans.core.ui.resources.Bundle` 31 键 / 27 中文
- 标准按钮：`CTL_OK=确定`、`CTL_CANCEL=取消`、`CTL_YES=是`、`CTL_NO=否`、`CTL_CLOSE=关闭`、`CTL_HelpName=帮助`
- 回滚：23 个 jar 备份哈希全部校验通过；Autopsy 重启 PID 38252、Responding、**0 SEVERE/FATAL**

---

## 13. 菜单栏最终修复：layer displayName（-R3，2026-11-22 16:40）

### 13.1 为什么 bundle 覆盖了菜单还是英文

第 12 节把 `Menu/View`、`Menu/Tools`、`Menu/Help` 等路径键写进了 `org.netbeans.core.ui.resources.Bundle`，jar 内实加载也确认是中文，但菜单仍显示英文。逐层排查后确认：

- NetBeans 的文件夹显示名由 `FileUtil.getFileDisplayName()` 决定，逻辑是**先看 `displayName` 属性，再查 `localizingBundle` + 路径键**；
- 属性链在多层 layer 合并、模块类加载器切换时会退化到「直接返回文件夹名」，实测 `XMLFileSystem` 探针就返回了 `Menu/View` 本身；
- 因此**只靠 bundle 不可靠**，必须把显示名写进 layer。

### 13.2 做法

`scripts/patch_layer_names.py` 直接改写 jar 内 `layer.xml`，给菜单文件夹插入字面量：

```xml
<folder name="View">
  <attr name="displayName" stringvalue="视图(&amp;V)"/>
  ...
```

覆盖 4 个 jar、16 处：

| jar | 写入 |
|---|---|
| `org-netbeans-core-ui.jar` | 文件/编辑/视图/导航/工具/帮助/网页/IDE 工具（8） |
| `org-netbeans-core-windows.jar` | 窗口（1） |
| `org-netbeans-modules-javahelp.jar` | 帮助（1） |
| `org-sleuthkit-autopsy-core.jar` | 案件/打开最近的案件/视图/工具/窗口/帮助（6） |

### 13.3 两个必须记住的坑

1. **XML 属性里的 `&` 必须转义成 `&amp;`**。第一次写入漏了转义，`&View` 直接让 layer.xml 变成非法 XML（`not well-formed line 198`），模块会加载失败。脚本已加 `xesc()`。
2. **空文件夹的边界**：`core-ui` 里的 `Menu/View` 是空文件夹（`</folder>` 紧跟），按「下一个 `<file>`」找属性区会越过它，误判成「已有 displayName」而跳过。改为取 `<file>` / `</folder>` / `<folder>` 三者最早的位置。

### 13.4 验收

- 4 个 jar `XML OK` + `zip=OK`；`loadtest_all.py` 仍 0 异常
- 从 layer 直接读出的最终显示名：`案件 / 视图(&V) / 工具(&T) / 窗口(&W) / 帮助(&H) / 打开最近的案件`
- Autopsy 重启 PID 28408、Responding、**0 SEVERE/FATAL**、无 layer 解析错误
- 回滚：`python scripts/patch_layer_names.py --restore` 可单独撤销 layer 补丁（备份在 `backups/layerpatch/`）

---

## 14. 菜单修复的三次返工与最终状态（2026-11-22 17:25）

### 14.1 为什么前两次没生效

| 版本 | 做法 | 失败原因 |
|---|---|---|
| v1 | 正则在 `resources/layer.xml` 里找 `<folder name="X">` 插入属性 | 同名文件夹存在多处（Toolbars/View、Shortcuts/View），插入落到**非菜单**的那个；`Menu/Case` 因名字唯一反而成功，造成「案件中文、其余英文」的假象 |
| v2/v3 | 按 `bundlevalue`/路径判定 + 正则定位 | 仍用文本正则，插入点落进 `<file name="...">` 属性值中间，layer.xml 直接非法；另 `displayName` 是**子元素** `<attr>`，脚本误判「不存在」而重复插入 |
| 另 | 只加 `_zh_CN` bundle | 该批 `Menu/*` 键直到 17:19 才真正注入 jar；17:05 的截图里根本没进 jar，故仍英文 |

### 14.2 最终做法（v4）

`scripts/patch_layer_names4.py`：

- 用 `xml.parsers.expat` 取 `<folder>` 真实字节偏移，**按层级栈还原完整路径**（`Menu/View` vs `Toolbars/View` 不再混淆）；
- 判断是否已有 `displayName` 时，扫描 folder 起始标签之后的**连续 `<attr>` 子元素块**，而非 XML 属性；
- 写入 `&` 转义后的中文，幂等（重复执行 0 写入）。

### 14.3 结果

- 13 个 jar、35 处 displayName；`Menu/Case|File|Edit|View|GoTo|Tools|Help|Window|Window/Tools|Window/Web` 全部覆盖
- 4 个菜单所属 layer 全部 `XML OK`、zip 完好；`loadtest_all.py` 0 异常
- 运行实例 PID 17288（17:20 启动）：`user.language=zh / user.country=CN`
- 独立验证：`NbBundle.getMessage(ToggleFullScreenAction.class,"CTL_ToggleFullScreenAction")` → **全屏(&F)**（此前认为平台 bundle 不生效，实为键未注入 jar 所致）

---

## 15. 菜单一直是英文的真正原因：NetBeans 的 layer 缓存（2026-11-22 18:20）

### 15.1 根因

NetBeans 把**合并后的 layer** 缓存在：

```
C:/Users/<user>/AppData/Local/autopsy/Cache/dev/all-layers.dat   ← 合并后的 layer（安装日 5 月生成）
C:/Users/<user>/AppData/Local/autopsy/Cache/dev/localeVariants   ← 语言变体索引
C:/Users/<user>/AppData/Local/autopsy/Cache/dev/all-resources.dat（204 MB）
```

**只要这个缓存还在，改 jar 里的 layer.xml（displayName / 改文件夹名）都不会被读取**，程序继续用缓存里的旧菜单结构。这也解释了此前所有「改完没变化」的现象：

- `Bundle_zh_CN.properties` 生效（资源走 classloader，不经过 layer 缓存）→ 启动窗口标题「欢迎」正常；
- 菜单名不生效（走 layer 缓存）→ View/Tools/Window/Help 恒为英文；
- 甚至把英文原文 `Bundle.properties` 全量改成中文也没用。

### 15.2 处置

1. 关闭 Autopsy。
2. 清空 `%LOCALAPPDATA%\autopsy\Cache\dev\*`。
3. 重新启动（首次启动会重建缓存，约 60–90 秒）。

效果（实测截图）：菜单栏由 `案件 View Tools Window Help` 变为 **`案件 视图(V) 工具(T) 窗口(W) 帮助(H)`**。

### 15.3 已固化到安装流程

`install_pack.py` 与 `apply_to_root.py` 安装完成后会**自动清理该缓存**（新增 `clear_nb_cache()`），并打印清理路径。以后重装语言包不必手工删缓存。

> 注意：两份 Autopsy 安装共用同一 userdir/cachedir（`%APPDATA%\autopsy`、`%LOCALAPPDATA%\autopsy\Cache`），切换安装后同样需要清缓存。

### 15.4 排错结论归档（避免重走弯路）

| 试过的做法 | 结果 | 说明 |
|---|---|---|
| 补 `Menu/*` 路径键到 `Bundle_zh_CN` | 无效 | layer 缓存遮蔽 |
| 给 folder 加 `displayName` 属性 | 缓存清理后**有效** | 属性方式正确，此前被缓存挡住 |
| 把英文原文 `Bundle.properties` 改成中文 | 无效 | `_zh_CN` 优先级更高，且菜单不经 bundle |
| 直接改文件夹名（`Menu/Help=帮助`） | 缓存清理后有效 | 但会与其它层的合并产生重复菜单，不推荐 |
