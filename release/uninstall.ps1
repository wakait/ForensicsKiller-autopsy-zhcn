# Autopsy 简体中文语言包 - 卸载脚本
# 从最近一次安装备份还原原始 jar，并清理 NetBeans 缓存。

param(
    [string]$Root = "",
    [switch]$DryRun,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
try { $null = cmd /c chcp 65001 } catch { }
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false) } catch { }
$logDir = Join-Path $env:LOCALAPPDATA "autopsy-zhcn"

function Write-Step($m) { Write-Host "[*] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[+] $m" -ForegroundColor Green }
function Write-Err($m)  { Write-Host "[x] $m" -ForegroundColor Red }

Write-Host ""
Write-Host "  Autopsy 简体中文语言包 - 卸载" -ForegroundColor White
Write-Host "  ------------------------------------" -ForegroundColor DarkGray

$running = Get-Process -Name "autopsy64" -ErrorAction SilentlyContinue
if ($running) { Write-Err "请先完全退出 Autopsy。"; Read-Host "按回车退出"; exit 1 }

if (-not (Test-Path $logDir)) { Write-Err "未找到安装备份目录：$logDir"; Read-Host "按回车退出"; exit 1 }
$backups = Get-ChildItem $logDir -Directory -Filter "backup-*" | Sort-Object Name -Descending
if ($backups.Count -eq 0) { Write-Err "没有可用的备份。"; Read-Host "按回车退出"; exit 1 }
$src = $backups[0].FullName
Write-Ok ("使用备份：" + $src)

if (-not $Root) {
    if ($env:AUTOPSY_HOME) { $Root = $env:AUTOPSY_HOME }
    elseif (Test-Path "D:\kit-ascii\autopsy\bin\autopsy64.exe") { $Root = "D:\kit-ascii\autopsy" }
    else { $Root = Read-Host "请输入 Autopsy 安装目录" }
}
if (-not (Test-Path (Join-Path $Root "bin\autopsy64.exe"))) { Write-Err "目录无效：$Root"; Read-Host "按回车退出"; exit 1 }

$files = Get-ChildItem $src -Recurse -File
Write-Step ("还原 {0} 个文件" -f $files.Count)
foreach ($f in $files) {
    $rel = $f.FullName.Substring($src.Length).TrimStart("\")
    $dst = Join-Path $Root $rel
    if ($DryRun) { Write-Host "    [dry] $rel" -ForegroundColor DarkGray; continue }
    Copy-Item $f.FullName $dst -Force
}
if (-not $DryRun) { Write-Ok "已还原" }

Write-Step "清理 NetBeans 缓存"
foreach ($d in @((Join-Path $env:LOCALAPPDATA "autopsy\Cache\dev"), (Join-Path $env:LOCALAPPDATA "autopsy\Cache"))) {
    if (Test-Path $d) {
        if (-not $DryRun) { Get-ChildItem $d -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue }
        Write-Ok "已清理：$d"
    }
}

Write-Host ""
if ($DryRun) { Write-Host "  [演练模式] 未修改任何文件。" -ForegroundColor Yellow }
else { Write-Host "  已卸载，Autopsy 恢复原界面。" -ForegroundColor Green }
Write-Host ""
if (-not $Quiet) { Read-Host "按回车退出" }
