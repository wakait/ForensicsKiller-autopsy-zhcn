# 发布说明（维护者用）

本文件写给**维护者**。终端用户请看发布包里的 `使用说明.txt`。

---

## 1. 发布物是什么

```
dist/Autopsy-4.23.1-zhCN-<版本>.zip      ≈ 0.3 MB
```

解压后：

```
Autopsy-4.23.1-zhCN-<版本>/
├─ 安装.bat            ← 双击安装
├─ 卸载.bat            ← 双击还原
├─ install.ps1         ← 实际执行体（PowerShell，Windows 自带，无需 Python）
├─ uninstall.ps1
├─ 使用说明.txt         ← 给终端用户
├─ 版本说明.txt
└─ payload/
   ├─ bundles.json     180 条：{jar, entry, file}
   ├─ layers.json      13 条：{jar, entry, file, expect(原始 layer 的 SHA256), added}
   ├─ b/b000..b179.properties    中文资源
   └─ l/*.xml                    打过菜单补丁的 layer 全文
```

**为什么不含完整 jar**：23 个目标 jar 共 46 MB，且对 Autopsy 小版本极敏感。改用「只下发资源 + 按需改 jar」，包体只有 0.3 MB，且带原始 layer 哈希校验，版本不符会自动跳过而不是搞坏安装。

---

## 2. 构建

```bat
:: 首次构建（需要原始 layer 备份）
python scripts\build_release.py --backup-root "<...>\backups\layerpatch_v4"

:: 之后只改了脚本/文案，复用已生成的 layer 补丁
python scripts\build_release.py --reuse
```

产物：

- `dist/Autopsy-4.23.1-zhCN-<版本>.zip`
- `dist/SHA256.txt`（发布时贴到 release 说明里）

构建时会：

1. 从备份里的**原始 layer** 应用 `patch_layer_names.rewrite()`，产出补丁后的 layer 全文与原始哈希；
2. 把 `locales/` 的 180 个资源复制成 `payload/b/*.properties`；
3. 组装 zip。

`release/layer_index.json` 与 `release/patched/l/*.xml` 是入库的中间产物，`--reuse` 时直接使用，因此**没有备份也能重新打包**。

---

## 3. 发布到 GitHub Releases（建议流程）

```bat
git tag v2026.12-FINAL-R3
git push origin v2026.12-FINAL-R3
```

然后在 GitHub 上 New release：

- Tag：`v2026.12-FINAL-R3`
- 标题：`Autopsy 4.23.1 简体中文语言包 R3`
- 附件：`dist/Autopsy-4.23.1-zhCN-v2026.12-FINAL-R3.zip`
- 正文模板见下

```markdown
## Autopsy 4.23.1 简体中文语言包 R3

开箱即用，无需安装 Python。下载 zip → 解压 → 双击「安装.bat」。

- 覆盖 180 个资源包、约 8900 条中文文案
- 菜单栏：案件 / 视图 / 工具 / 窗口 / 帮助
- 含卸载脚本，自动备份，可完整还原

SHA256: <填入 dist/SHA256.txt 中的值>

**注意**：仅适配 Autopsy 4.23.1；安装前请完全退出 Autopsy。
安装后首次启动会重建缓存，约 60–90 秒。
```

---

## 4. 版本号规则

- 资源版本 `v2026.12-FINAL`，补丁号 `-R1`、`-R2`、`-R3` 递增。
- 改动文案 / 新增 bundle → 递增补丁号并重新打包。
- 适配新 Autopsy 版本 → 新建版本目录，**不要**在旧包上改。

---

## 5. 发布前检查清单

- [ ] `python scripts/verify_new.py` → 0 FAIL
- [ ] `python scripts/loadtest_all.py` → 全部通过、异常 0
- [ ] `python scripts/build_release.py --reuse` 成功，记录 SHA256
- [ ] 解压 zip，对**测试目录**跑 `install.ps1 -Root <测试目录> -Quiet`，确认：
      jar 内出现 `Bundle_zh_CN.properties`、layer 出现 `视图`、`autopsy.conf` 含中文参数
- [ ] 跑 `uninstall.ps1 -Root <测试目录> -Quiet`，确认三者均还原
- [ ] 真机安装后启动 Autopsy，截图确认菜单为 `案件 视图 工具 窗口 帮助`
