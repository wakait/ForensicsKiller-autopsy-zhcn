# Autopsy 简体中文语言包 - 安装脚本（无需 Python）
# 用法：右键“使用 PowerShell 运行”，或在命令行执行：
#   powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1
# 参数：-Root "D:\...\autopsy"   指定安装目录（不填则自动探测）

param(
    [string]$Root = "",
    [switch]$DryRun,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
try { $null = cmd /c chcp 65001 } catch { }
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false) } catch { }
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$payload = Join-Path $here "payload"
$logDir = Join-Path $env:LOCALAPPDATA "autopsy-zhcn"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $logDir ("backup-" + $stamp)

function Write-Step($msg) { Write-Host "[*] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "[+] $msg" -ForegroundColor Green }
function Write-Warn2($msg){ Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[x] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "  Autopsy 简体中文语言包 安装程序" -ForegroundColor White
Write-Host "  ------------------------------------" -ForegroundColor DarkGray
Write-Host ""

# ---------- 1. 定位安装目录 ----------
function Find-Autopsy {
    $cands = @()
    if ($Root) { $cands += $Root }
    if ($env:AUTOPSY_HOME) { $cands += $env:AUTOPSY_HOME }
    $cands += @(
        "D:\kit-ascii\autopsy",
        "C:\Program Files\Autopsy-4.23.1",
        "C:\Program Files\Autopsy"
    )
    foreach ($c in $cands) {
        if ($c -and (Test-Path (Join-Path $c "bin\autopsy64.exe"))) { return (Resolve-Path $c).Path }
    }
    # 常见根目录浅层扫描
    foreach ($drv in @("C:","D:","E:")) {
        if (-not (Test-Path $drv)) { continue }
        $hit = Get-ChildItem -Path $drv -Filter "autopsy64.exe" -Recurse -Depth 4 -ErrorAction SilentlyContinue |
               Select-Object -First 1
        if ($hit) { return (Split-Path -Parent (Split-Path -Parent $hit.FullName)) }
    }
    return ""
}

if (-not $Root) {
    Write-Step "正在查找 Autopsy 安装目录..."
    $Root = Find-Autopsy
}
if (-not $Root -or -not (Test-Path (Join-Path $Root "bin\autopsy64.exe"))) {
    Write-Err "未找到 Autopsy 安装目录。"
    Write-Host "    请用参数指定，例如：" -ForegroundColor Gray
    Write-Host '    powershell -ExecutionPolicy Bypass -File install.ps1 -Root "D:\kit-ascii\autopsy"' -ForegroundColor Gray
    if (-not $Quiet) { Read-Host "按回车退出" }
    exit 1
}
Write-Ok "安装目录：$Root"

# ---------- 2. 检查进程 ----------
$running = Get-Process -Name "autopsy64" -ErrorAction SilentlyContinue
if ($running) {
    Write-Err "检测到 Autopsy 正在运行，请先完全退出后再安装。"
    if (-not $Quiet) { Read-Host "按回车退出" }
    exit 1
}

# ---------- 3. 读取清单 ----------
$bundlesJson = Join-Path $payload "bundles.json"
$layersJson  = Join-Path $payload "layers.json"
if (-not (Test-Path $bundlesJson)) { Write-Err "安装包不完整：缺少 payload/bundles.json"; Read-Host "按回车退出"; exit 1 }
$bundles = Get-Content $bundlesJson -Raw -Encoding UTF8 | ConvertFrom-Json
$layers  = @()
if (Test-Path $layersJson) { $layers = Get-Content $layersJson -Raw -Encoding UTF8 | ConvertFrom-Json }

if (-not $DryRun) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
}

function Add-ZipEntry($jarPath, $entryName, $srcFile) {
    $zip = [System.IO.Compression.ZipFile]::Open($jarPath, "Update")
    try {
        $old = $zip.GetEntry($entryName)
        if ($old) { $old.Delete() }
        $entry = $zip.CreateEntry($entryName, [System.IO.Compression.CompressionLevel]::Optimal)
        $stream = $entry.Open()
        try {
            $bytes = [System.IO.File]::ReadAllBytes($srcFile)
            $stream.Write($bytes, 0, $bytes.Length)
        } finally { $stream.Close() }
    } finally { $zip.Dispose() }
}

function Get-ZipEntryHash($jarPath, $entryName) {
    $zip = [System.IO.Compression.ZipFile]::OpenRead($jarPath)
    try {
        $e = $zip.GetEntry($entryName)
        if (-not $e) { return "" }
        $ms = New-Object System.IO.MemoryStream
        $s = $e.Open()
        $s.CopyTo($ms)
        $s.Close()
        $bytes = $ms.ToArray()
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $hash = $sha.ComputeHash($bytes)
        return ([BitConverter]::ToString($hash) -replace "-", "").ToLower()
    } finally { $zip.Dispose() }
}

# ---------- 4. 备份 ----------
$jarSet = @{}
foreach ($b in $bundles) { $jarSet[$b.jar] = $true }
foreach ($l in $layers)  { $jarSet[$l.jar] = $true }

if (-not $DryRun) {
    Write-Step "备份原始 jar（$($jarSet.Count) 个）到：$backupDir"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    foreach ($j in $jarSet.Keys) {
        $rel = $j -replace "\\", "\"
        $src = Join-Path $Root $rel
        if (Test-Path $src) {
            $dst = Join-Path $backupDir $rel
            $dstDir = Split-Path -Parent $dst
            if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
            Copy-Item $src $dst -Force
        }
    }
    Write-Ok "备份完成"
}

# ---------- 5. 写入中文资源 ----------
Write-Step "写入中文资源文件..."
$okCount = 0; $skipCount = 0
foreach ($b in $bundles) {
    $jarPath = Join-Path $Root ($b.jar -replace "\\", "\")
    $srcFile = Join-Path $payload $b.file
    if (-not (Test-Path $jarPath)) { Write-Warn2 "跳过（无此 jar）：$($b.jar)"; $skipCount++; continue }
    if (-not (Test-Path $srcFile)) { Write-Warn2 "跳过（载荷缺失）：$($b.file)"; $skipCount++; continue }
    if ($DryRun) { $okCount++; continue }
    try { Add-ZipEntry $jarPath $b.entry $srcFile; $okCount++ }
    catch { Write-Warn2 ("写入失败 {0}：{1}" -f $b.jar, $_.Exception.Message); $skipCount++ }
}
Write-Ok ("资源写入完成：成功 {0} 个，跳过 {1} 个" -f $okCount, $skipCount)

# ---------- 6. 应用菜单补丁 ----------
if ($layers.Count -gt 0) {
    Write-Step "应用菜单显示名补丁..."
    $lOk = 0; $lSkip = 0
    foreach ($l in $layers) {
        $jarPath = Join-Path $Root ($l.jar -replace "\\", "\")
        if (-not (Test-Path $jarPath)) { $lSkip++; continue }
        $cur = ""
        if (-not $DryRun) { $cur = Get-ZipEntryHash $jarPath $l.entry }
        if (-not $DryRun -and $cur -ne $l.expect) {
            Write-Warn2 ("跳过菜单补丁（{0} 的 layer 与本包基线不一致，可能版本不同）" -f (Split-Path -Leaf $jarPath))
            $lSkip++; continue
        }
        if ($DryRun) { $lOk++; continue }
        try {
            Add-ZipEntry $jarPath $l.entry (Join-Path $payload $l.file)
            $lOk++
        } catch { Write-Warn2 ("菜单补丁失败 {0}：{1}" -f $jarPath, $_.Exception.Message); $lSkip++ }
    }
    Write-Ok ("菜单补丁：成功 {0} 个，跳过 {1} 个" -f $lOk, $lSkip)
}

# ---------- 7. 设置界面语言 ----------
Write-Step "设置界面语言为简体中文..."
$conf = Join-Path $Root "AppDataFolder\autopsy\etc\autopsy.conf"
if (Test-Path $conf) {
    $text = Get-Content $conf -Raw -Encoding UTF8
    if ($text -match "-J-Duser\.language=zh") {
        Write-Ok "autopsy.conf 已包含中文参数"
    } else {
        $idx = $text.IndexOf('default_options="')
        if ($idx -ge 0) {
            $close = $text.IndexOf('"', $idx + 17)
            if ($close -gt 0) {
                $new = $text.Substring(0, $close) + " -J-Duser.language=zh -J-Duser.country=CN" + $text.Substring($close)
                if (-not $DryRun) {
                    $confBak = Join-Path $backupDir "AppDataFolder\autopsy\etc\autopsy.conf"
                    $confBakDir = Split-Path -Parent $confBak
                    if (-not (Test-Path $confBakDir)) { New-Item -ItemType Directory -Path $confBakDir -Force | Out-Null }
                    Copy-Item $conf $confBak -Force -ErrorAction SilentlyContinue
                    [System.IO.File]::WriteAllText($conf, $new, (New-Object System.Text.UTF8Encoding($false)))
                }
                Write-Ok "已写入中文语言参数"
            }
        } else { Write-Warn2 "未找到 default_options，跳过（界面可能仍为英文）" }
    }
} else { Write-Warn2 "未找到 autopsy.conf，跳过语言参数设置" }

# ---------- 8. 清理 NetBeans layer 缓存 ----------
Write-Step "清理 NetBeans 菜单缓存（关键步骤）..."
$cacheDirs = @(
    (Join-Path $env:LOCALAPPDATA "autopsy\Cache\dev"),
    (Join-Path $env:LOCALAPPDATA "autopsy\Cache")
)
foreach ($d in $cacheDirs) {
    if (Test-Path $d) {
        if (-not $DryRun) { Get-ChildItem $d -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue }
        Write-Ok "已清理：$d"
    }
}

# ---------- 9. 完成 ----------
Write-Host ""
if ($DryRun) {
    Write-Host "  [演练模式] 未修改任何文件。" -ForegroundColor Yellow
} else {
    Write-Host "  安装完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "  启动 Autopsy 即可看到中文界面。" -ForegroundColor White
    Write-Host "  首次启动会重建缓存，约需 60-90 秒，请耐心等待。" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  如需卸载：运行 卸载.bat" -ForegroundColor Gray
    Write-Host "  备份位置：$backupDir" -ForegroundColor DarkGray
}
Write-Host ""
if (-not $Quiet) { Read-Host "按回车退出" }
