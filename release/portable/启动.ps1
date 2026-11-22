# Autopsy 简体中文便携版 - 启动脚本
# 作用：清理过一次 NetBeans 菜单缓存后启动 Autopsy（缓存只有首次需要重建）
param([switch]$Force)

$ErrorActionPreference = "Stop"
try { $null = cmd /c chcp 65001 } catch { }
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false) } catch { }

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $here "autopsy\bin\autopsy64.exe"
if (-not (Test-Path $exe)) {
    $exe = Join-Path $here "bin\autopsy64.exe"
}
if (-not (Test-Path $exe)) {
    Write-Host "[x] 找不到 autopsy64.exe，请确认解压完整。" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}

$markerDir = Join-Path $env:LOCALAPPDATA "autopsy-zhcn"
$marker = Join-Path $markerDir "portable-cache.tag"
$version = "2026.12-FINAL-R3"
$needClear = $Force
if (-not $needClear) {
    if (-not (Test-Path $marker)) { $needClear = $true }
    elseif ((Get-Content $marker -Raw -ErrorAction SilentlyContinue).Trim() -ne $version) { $needClear = $true }
}

if ($needClear) {
    Write-Host "[*] 首次运行，正在清理菜单缓存（约 60-90 秒后自动进入）..." -ForegroundColor Cyan
    foreach ($d in @((Join-Path $env:LOCALAPPDATA "autopsy\Cache\dev"), (Join-Path $env:LOCALAPPDATA "autopsy\Cache"))) {
        if (Test-Path $d) {
            Get-ChildItem $d -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    New-Item -ItemType Directory -Path $markerDir -Force | Out-Null
    Set-Content -Path $marker -Value $version -Encoding ASCII
}

Start-Process -FilePath $exe -WorkingDirectory (Split-Path -Parent $exe)
