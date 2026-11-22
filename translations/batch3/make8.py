import json
from pathlib import Path

B = Path(r"E:/Snow/Desktop/workspace/2026/取证/决赛备战/autopsy-zhCN-v2026.12-FINAL/.batch3")
D = {}

D["osaccount"] = {
    "OsAccountDataPanel_basic_creationDate": "创建日期",
    "OsAccountDataPanel_basic_fullname": "全名",
    "OsAccountDataPanel_basic_objId": "对象 ID",
    "OsAccountDataPanel_basic_title": "基本属性",
    "OsAccountDataPanel_data_accessed_title": "最后登录",
    "OsAccountDataPanel_host_count_title": "登录次数",
    "OsAccountDataPanel_realm_title": "领域属性",
    "OsAccountViewer_title": "操作系统账户",
    "OsAccountViewer_tooltip": "查看与所选节点相关的操作系统账户。",
}

D["menuactions"] = {
    "DataContentDynamicMenu.contentViewers.text": "内容查看器",
    "DataContentDynamicMenu.menu.dataContentWin.text": "数据内容窗口",
    "DataContentMenu.getName.text": "数据内容菜单",
    "DataExplorerMenu.getName.text": "数据浏览工具",
    "DataResultMenu.menu.dataResWin.text": "数据结果窗口",
    "DataResultMenu.getName.text": "数据结果菜单",
    "SearchResultMenu.menu.dataRes.text": "数据结果",
    "SearchResultMenu.resultViewers.text": "结果查看器",
}

D["runingestmodulewizard"] = {
    "IngestModulesConfigWizardPanel.name.text": "配置摄取模块",
    "IngestProfileSelectionPanel.customSettings.description": "在向导的下一步中配置各模块设置",
    "IngestProfileSelectionPanel.customSettings.name": "自定义设置",
    "IngestProfileSelectionPanel.ingestSettingsButton.text": "摄取设置",
    "IngestProfileSelectionPanel.profileListLabel.text": "选择配置文件：",
    "IngestProfileWizardPanel.panelName": "摄取配置文件选择",
    "RunIngestModulesAction.actionPerformed.errorMessage": "查询所选项目的案例数据库时出错。",
    "RunIngestModulesAction.name": "运行摄取模块",
}

D["imagegallery-datamodel"] = {
    "DrawableAttribute.cameraMake": "相机厂商",
    "DrawableAttribute.cameraModel": "相机型号",
    "DrawableAttribute.createdTime": "创建时间",
    "DrawableAttribute.intObjID": "内部对象 ID",
    "DrawableAttribute.md5hash": "MD5 哈希",
    "DrawableAttribute.mimeType": "MIME 类型",
    "DrawableAttribute.modifiedTime": "修改时间",
    "VideoFile.getMedia.progress": "正在把临时文件写入磁盘",
}

D["multiusercasesbrowser"] = {
    "MultiUserCaseBrowserCustomizer.column.caseDbDeleteStatus": "案例数据库已删除",
    "MultiUserCaseBrowserCustomizer.column.caseDirDeleteStatus": "案例目录已删除",
    "MultiUserCaseBrowserCustomizer.column.createTime": "创建时间",
    "MultiUserCaseBrowserCustomizer.column.dataSourcesDeleteStatus": "数据源已删除",
    "MultiUserCaseBrowserCustomizer.column.lastAccessTime": "最后访问时间",
    "MultiUserCaseBrowserCustomizer.column.manifestFileZNodesDeleteStatus": "清单 Znode 已删除",
    "MultiUserCaseBrowserCustomizer.column.textIndexDeleteStatus": "文本索引已删除",
    "MultiUserCasesBrowserPanel.waitNode.message": "请稍候...",
}

D["centralrepository"] = {
    "AddEditCentralRepoCommentAction.menuItemText.addEditCentralRepoComment": "添加/编辑中央存储库备注",
    "AddEditCentralRepoCommentAction.menuItemText.addEditCentralRepoCommentEmptyFile": "添加/编辑中央存储库备注（空文件）",
    "AddEditCentralRepoCommentAction.menuItemText.addEditCentralRepoCommentNoMD5": "添加/编辑中央存储库备注（无 MD5 哈希）",
    "CentralRepoCommentDialog.title.addEditCentralRepoComment": "添加/编辑中央存储库备注",
    "OpenIDE-Module-Name": "中央存储库",
    "OpenIDE-Module-Display-Category": "摄取模块",
    "OpenIDE-Module-Short-Description": "中央存储库摄取模块",
}

D["zooming"] = {
    "EventTypeZoomLevel.rootType": "根类型",
    "EventTypeZoomLevel.baseType": "基础类型",
    "EventTypeZoomLevel.subType": "子类型",
    "ZoomSettingsPane.descrLODLabel.text": "描述详细程度：",
    "ZoomSettingsPane.sliderChange.errorText": "响应滑块值变化时出错。",
    "ZoomSettingsPane.timeUnitLabel.text": "时间单位：",
    "ZoomSettingsPane.typeZoomLabel.text": "事件类型：",
}

D["bodyfile"] = {
    "ReportBodyFile.progress.querying": "正在查询文件...",
    "ReportBodyFile.ingestWarning.text": "警告：该报告在摄取服务完成之前已运行\\!",
    "ReportBodyFile.progress.loading": "正在加载文件...",
    "ReportBodyFile.progress.processing": "正在处理 {0}...",
    "ReportBodyFile.getName.text": "TSK Body 文件",
    "ReportBodyFile.getDesc.text": "Body 文件格式的报告，包含每个文件的 MAC 时间。该格式可用于时间线视图。",
    "ReportBodyFile.generateReport.srcModuleName.text": "TSK Body 文件",
}

D["objectdetection"] = {
    "ObjectDetectionFileIngestModule.classifierDetection.text": "分类器检测到 {0} 个对象",
    "ObjectDetectionFileIngestModule.noClassifiersFound.message": "在 {0} 中未找到分类器，不会执行对象检测。",
    "ObjectDetectionFileIngestModule.noClassifiersFound.subject": "未找到分类器。",
    "ObjectDetectionFileIngestModule.notWindowsError": "该模块仅在 Windows 上可用。",
    "ObjectDetectionFileIngestModule.openCVNotLoaded": "OpenCV 未加载，但运行该模块需要它。",
    "ObjectDetectionModuleFactory.moduleDescription.text": "使用对象分类器识别图片中的对象。",
    "ObjectDetectionModuleFactory.moduleName.text": "对象检测",
}

for name, mapping in D.items():
    p = B / (name + ".json")
    p.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", p.name, len(mapping))
