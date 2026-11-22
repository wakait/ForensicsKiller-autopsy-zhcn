import json
from pathlib import Path

B = Path(r"E:/Snow/Desktop/workspace/2026/取证/决赛备战/autopsy-zhCN-v2026.12-FINAL/.batch3")
D = {}

D["eventlisteners"] = {
    "CentralRepositoryNotificationDialog.bulletHeader": "这些数据用于：",
    "CentralRepositoryNotificationDialog.bulletOne": "忽略常见项目（文件、域名和账户）",
    "CentralRepositoryNotificationDialog.bulletThree": "创建用于归组账户的人员档案",
    "CentralRepositoryNotificationDialog.bulletTwo": "识别某项目此前在何处出现过",
    "CentralRepositoryNotificationDialog.finalRemarks": "如需限制存储内容，请使用中央存储库选项面板。",
    "CentralRepositoryNotificationDialog.header": "Autopsy 会把每个案例的数据存储到中央存储库中。",
    "Installer.centralRepoUpgradeFailed.title": "中央存储库已禁用",
}

D["datamodel-tail"] = {
    "AbstractAbstractFileNode.md5HashColLbl": "MD5 哈希",
    "AbstractAbstractFileNode.sha256HashColLbl": "SHA-256 哈希",
    "BlackboardArtifactNode.createSheet.artifactMD5.displayName": "MD5 哈希",
    "BlackboardArtifactNode.createSheet.artifactMD5.name": "MD5 哈希",
    "ContentTagNode.createSheet.artifactMD5.displayName": "MD5 哈希",
    "ContentTagNode.createSheet.artifactMD5.name": "MD5 哈希",
}

D["reportmain"] = {
    "DefaultReportConfigurationPanel.infoLabel.text": "该报告将在下一个界面中配置。",
    "ReportBranding.defaultReportTitle.text": "Autopsy 取证报告",
    "ReportBranding.defaultReportFooter.text": "由 Autopsy 开源数字取证平台提供支持 - www.sleuthkit.org",
    "ReportProgressPanel.initPathLabel.noFile": "<html><u>没有报告文件</u></html>",
    "ReportProgressPanel.start.progress.text": "正在启动报告...",
    "ReportProgressPanel.complete.processLb2.text": "已完成，但有错误",
}

D["examples"] = {
    "SampleIngestModuleFactory.moduleName": "示例摄取模块",
    "SampleIngestModuleFactory.moduleDescription": "该模块是供软件开发人员参考的示例摄取模块。",
    "SampleIngestModuleIngestJobSettingsPanel.skipKnownFilesCheckBox.text": "跳过已知文件（NSRL）",
    "SampleExecutableIngestModuleFactory.moduleName": "示例可执行文件摄取模块",
    "SampleExecutableIngestModuleFactory.moduleDescription": "该模块是供软件开发人员参考的示例可执行文件摄取模块。",
}

D["imagewriter"] = {
    "ImageWriter.progressBar.message": "正在完成 {0} 的采集（拔出设备可取消）",
    "ImageWriterService.serviceName": "映像写入器",
    "ImageWriterService.waitingForVHDs": "正在等待 VHD 完成",
    "ImageWriterService.shouldWait": "是否等待进行中的 VHD 完成？",
    "ImageWriterService.localDisk": "本地磁盘映像复制",
}

D["timeline-filtering"] = {
    "FilsetSetPanel.hiddenDescriptionsPane.displayName": "已隐藏的描述",
    "FilterSetPanel.applyButton.longText": "（重新）应用筛选器",
    "FilterSetPanel.hiddenDescriptionsListView.remove": "从列表中移除",
    "FilterSetPanel.hiddenDescriptionsListView.unhideAndRemove": "取消隐藏并从列表中移除",
    "Timeline.ui.filtering.promptText": "输入筛选字符串",
}

D["yara"] = {
    "Yara_Module_Description": "YARA 分析器使用 YARA 在文件中搜索文本或二进制模式。",
    "Yara_Module_Name": "YARA 分析器",
    "YaraIngestModule_no_ruleSets": "无法运行 YARA 摄取：YARA 规则集列表为空。",
    "YaraIngestModule_windows_error_msg": "YARA 摄取模块仅在 64 位 Windows 上可用。",
    "YaraIngestModule_yarac_not_found": "无法编译 YARA 规则文件：在以下位置找不到可执行文件：",
}

D["dsuiutils"] = {
    "AbstractLoadableComponent_errorMessage_defaultText": "加载结果时出错。",
    "AbstractLoadableComponent_loadingMessage_defaultText": "正在加载结果...",
    "AbstractLoadableComponent_noDataExists_defaultText": "不存在数据。",
    "IngestRunningLabel_defaultMessage": "摄取正在运行。",
    "PieChartPanel_noDataLabel": "无数据",
}

D["analysisresults"] = {
    "AnalysisResultsContentPanel_aggregateScore_displayKey": "综合评分",
    "AnalysisResultsContentPanel_result_headerKey": "分析结果 {0}",
    "AnalysisResultsContentViewer_setNode_errorMessage": "加载结果时出错。",
    "AnalysisResultsContentViewer_title": "分析结果",
    "AnalysisResultsContentViewer_tooltip": "查看与所选节点相关的分析结果。",
}

D["guiutils"] = {
    "CheckBoxListPanel.checkButton.text": "全部勾选",
    "CheckBoxListPanel.uncheckButton.text": "全部取消勾选",
    "StatusIconCellRenderer.tooltiptext.error": "发生错误",
    "StatusIconCellRenderer.tooltiptext.warning": "发生警告",
}

D["python"] = {
    "JythonModuleLoader.errorMessages.failedToOpenModule": "无法打开 {0}。详情请查看日志。",
    "JythonModuleLoader.errorMessages.failedToLoadModule": "无法加载 {0}。{1}。详情请查看日志。",
    "JythonModuleLoader.pythonInterpreterError.msg": "无法加载 Python 模块，详情请查看日志",
    "JythonModuleLoader.pythonInterpreterError.title": "Python 模块",
}

D["explorernodes"] = {
    "EventNode.getAction.errorTitle": "获取操作时出错",
    "EventNode.getAction.linkedFileMessage": "获取所选结果的操作时出现问题。“在时间线中查看文件”操作将不可用。",
    "EventRoodNode.tooManyNode.displayName": "事件过多，无法显示。上限为 {0}，但有 {1} 个待显示。",
    "NodeProperty.displayName.eventType": "事件类型",
}

D["reportfile"] = {
    "ReportFileTextConfigurationPanel.tabDelimitedButton.text": "制表符分隔",
    "ReportFileTextConfigurationPanel.commaDelimitedButton.text": "逗号分隔",
    "FileReportText.getName.text": "文件 - 文本",
    "FileReportText.getDesc.text": "包含案例中各文件信息的分隔符文本文件。",
}

D["drones"] = {
    "DATExtractor_process_message": "正在处理 DJI DAT 文件：%s",
    "DATFileExtractor_Extractor_Name": "DAT 文件提取器",
    "DroneIngestModule_Description": "分析部分 DJI 无人机生成的文件。",
    "DroneIngestModule_Name": "DJI 无人机分析器",
}

D["test"] = {
    "CustomArtifactsCreatorDataSourceIngestModule.exceptionMessage.errorCreatingCustomType": "创建自定义产物类型时出错。",
    "CustomArtifactsCreatorFileIngestModule.exceptionMessage.errorCreatingCustomType": "创建自定义产物类型时出错。",
    "InterestingArtifactCreatorIngestModule.exceptionMessage.errorCreatingCustomType": "创建自定义产物类型时出错。",
}

D["recentactivity-windows"] = {
    "ExtractThumbcache_module_name": "缩略图缓存分析器",
    "Thumbcache_Files_Not_Found": "未找到缩略图缓存文件",
    "Thumbcache_process_error_executing_export_thumbcache_program": "运行缩略图缓存程序时出错",
}

D["pictureanalyzer"] = {
    "PictureAnalyzerIngestModule.cannot_run_file_type": "无法运行文件类型检测。",
    "PictureAnalyzerIngestModuleFactory.module_description": "对图片文件进行常规分析，包括提取 EXIF 元数据以及在格式之间转换。",
    "PictureAnalyzerIngestModuleFactory.module_name": "图片分析器",
}

D["grouping"] = {
    "GroupSortBy.groupName": "分组名称",
    "GroupSortBy.groupSize": "分组大小",
    "ReGroupTask.displayTitle": "正在按 {0} 重新分组：",
}

D["creapplication"] = {
    "OtherOccurrences.csvHeader.attribute": "匹配的属性",
    "OtherOccurrences.csvHeader.dataSource": "数据源",
    "OtherOccurrences.csvHeader.value": "属性值",
}

D["machinesettings"] = {
    "UserMachinePreferences_validateTempDirectory_errorOnCreate_text": "为以下路径创建临时目录时出错：{0}",
    "UserMachinePreferences_validateTempDirectory_errorOnReadWrite_text": "读写以下临时目录路径时出错：{0}",
}

D["textextractors"] = {
    "AbstractFileTikaTextExtract.index.tikaParseTimeout.text": "异常：内容 {0}、{1} 的 Tika 解析超时",
    "AbstractFileTikaTextExtract.index.exception.tikaParse.msg": "异常：对文件 {0}、{1} 执行 Tika 解析任务时出现意外异常",
}

D["ds-summary-datamodel"] = {
    "DataSourceUserActivitySummary_getRecentAccounts_calllogMessage": "通话记录",
    "DataSourceUserActivitySummary_getRecentAccounts_emailMessage": "电子邮件",
}

D["comm"] = {
    "VisualizationPanel.jButton1.text": "快速有机布局",
}

D["cci"] = {
    "CoreComponentControl.CTL_DirectoryTreeTopComponent": "目录树",
}

D["tree"] = {
    "EventsTree.Label.text": "排序依据：",
}

D["picimpls"] = {
    "ExifProcessor.userContent.description": "该文件存在 EXIF 元数据。",
}

D["ksinfra"] = {
    "NoReportConfigurationPanel.infoLabel.text": "该报告无需配置。",
}

for name, mapping in D.items():
    p = B / (name + ".json")
    p.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", p.name, len(mapping))
