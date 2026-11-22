# Autopsy 4.23.1 简体中文版 - 一键安装（引导安装器）
# 做四件事：下载官方 MSI → 静默安装 → 套用中文语言包 → 创建桌面快捷方式 → 自检
#
# 参数：
#   -Target "D:\Autopsy"   安装目录（默认 C:\Program Files\Autopsy-4.23.1）
#   -Msi "D:\xxx.msi"      使用本地已下载的 MSI（跳过下载）
#   -SkipDownload          只用本地缓存，不联网
#   -SkipInstall           跳过安装，仅套中文包（已装 Autopsy 时用）
#   -NoShortcut            不创建桌面快捷方式
#   -NoElevate             不自动提权（测试用）
#   -Quiet                 不等待回车

param(
    [string]$Target = "",
    [string]$Msi = "",
    [switch]$SkipDownload,
    [switch]$SkipInstall,
    [switch]$NoShortcut,
    [switch]$NoElevate,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
try { $null = cmd /c chcp 65001 } catch { }
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false) } catch { }

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$payload = Join-Path $here "payload"
$msiUrl = "https://github.com/sleuthkit/autopsy/releases/download/autopsy-4.23.1/autopsy-4.23.1-64bit.msi"
$msiSize = 1289204224
$msiCache = Join-Path $env:TEMP "autopsy-4.23.1-64bit.msi"
$logDir = Join-Path $env:LOCALAPPDATA "autopsy-zhcn"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $logDir ("backup-" + $stamp)

function Step($m) { Write-Host ""; Write-Host "[*] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "[+] $m" -ForegroundColor Green }
function Warn2($m){ Write-Host "[!] $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "[x] $m" -ForegroundColor Red }

function Stop-Here($code) {
    Write-Host ""
    if (-not $Quiet) { Read-Host "按回车退出" }
    exit $code
}

Write-Host ""
Write-Host "  ============================================" -ForegroundColor DarkGray
Write-Host "   Autopsy 4.23.1 简体中文版  一键安装" -ForegroundColor White
Write-Host "  ============================================" -ForegroundColor DarkGray

# ---------- 0. 环境检查 ----------
Step "检查运行环境"

$is64 = [Environment]::Is64BitOperatingSystem
if (-not $is64) { Fail "Autopsy 4.23.1 仅支持 64 位 Windows"; Stop-Here 1 }
Ok "64 位系统"

$osVer = [Environment]::OSVersion.Version
if ($osVer.Major -lt 10) { Warn2 ("Windows 版本较低（{0}），可能不受支持" -f $osVer) } else { Ok ("Windows {0}" -f $osVer) }

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) { Ok "管理员权限" } else { Warn2 "非管理员运行" }

if (-not $Target) { $Target = Join-Path $env:ProgramFiles "Autopsy-4.23.1" }

if (-not $SkipInstall) {
    $drive = (Split-Path -Qualifier $Target)
    if ($drive) {
        $free = (Get-PSDrive -Name $drive.TrimEnd(':') -ErrorAction SilentlyContinue).Free
        if ($free -and $free -lt 6GB) { Fail ("目标盘剩余空间不足（{0:N1} GB，至少需要 6 GB）" -f ($free/1GB)); Stop-Here 1 }
        if ($free) { Ok ("目标盘可用空间 {0:N1} GB" -f ($free/1GB)) }
    }
    if (-not $isAdmin -and -not $NoElevate) {
        Warn2 "安装到系统目录需要管理员权限，正在申请提权..."
        $argList = @("-NoProfile","-ExecutionPolicy","Bypass","-File",('"{0}"' -f $MyInvocation.MyCommand.Path),
                     "-Target",('"{0}"' -f $Target))
        if ($Msi) { $argList += @("-Msi", ('"{0}"' -f $Msi)) }
        if ($SkipDownload) { $argList += "-SkipDownload" }
        if ($NoShortcut) { $argList += "-NoShortcut" }
        try {
            Start-Process -FilePath "powershell.exe" -ArgumentList $argList -Verb RunAs -Wait
            exit 0
        } catch {
            Warn2 "提权失败，将继续以当前权限尝试安装（可能失败）"
        }
    }
}

# ---------- 1. 获取 MSI ----------
if (-not $SkipInstall) {
    Step "准备官方安装包"

    if (-not $Msi) {
        if (Test-Path $msiCache) {
            $sz = (Get-Item $msiCache).Length
            if ($sz -eq $msiSize) { Ok ("使用已缓存安装包：{0:N0} 字节" -f $sz); $Msi = $msiCache }
            else { Warn2 ("缓存文件大小不符（{0}），将重新下载" -f $sz); Remove-Item $msiCache -Force -ErrorAction SilentlyContinue }
        }
    }

    if (-not $Msi) {
        if ($SkipDownload) { Fail "已指定 -SkipDownload，但本地没有可用 MSI"; Stop-Here 1 }
        Ok ("开始下载（{0:N0} MB，视网速可能需要几分钟）" -f ($msiSize/1MB))
        Write-Host "    来源：$msiUrl" -ForegroundColor DarkGray
        $oldProgress = $ProgressPreference
        $ProgressPreference = "Continue"
        try {
            Invoke-WebRequest -Uri $msiUrl -OutFile $msiCache -UseBasicParsing -TimeoutSec 3600
        } catch {
            Fail ("下载失败：{0}" -f $_.Exception.Message)
            Write-Host "    可手动下载后使用参数 -Msi `"路径`" 指定：" -ForegroundColor Gray
            Write-Host "    $msiUrl" -ForegroundColor Gray
            Stop-Here 1
        } finally {
            $ProgressPreference = $oldProgress
        }
        $sz = (Get-Item $msiCache).Length
        if ($sz -ne $msiSize) { Fail ("下载不完整（{0:N0} / {1:N0} 字节）" -f $sz, $msiSize); Stop-Here 1 }
        Ok ("下载完成：{0:N0} MB" -f ($sz/1MB))
        $Msi = $msiCache
    }
    if (-not (Test-Path $Msi)) { Fail "找不到 MSI：$Msi"; Stop-Here 1 }
}

# ---------- 2. 静默安装 ----------
$installedRoot = ""
if (-not $SkipInstall) {
    Step ("静默安装到：{0}" -f $Target)
    if (-not (Test-Path $Target)) { New-Item -ItemType Directory -Path $Target -Force | Out-Null }
    $msiLog = Join-Path $logDir ("msi-" + $stamp + ".log")
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null

    $args = @("/i", ('"{0}"' -f $Msi), "/qn", "/norestart",
              ('APPDIR="{0}"' -f $Target), ('INSTALLDIR="{0}"' -f $Target),
              ('TARGETDIR="{0}"' -f $Target), "/L*v", ('"{0}"' -f $msiLog))
    Write-Host "    msiexec $($args -join ' ')" -ForegroundColor DarkGray
    $p = Start-Process -FilePath "msiexec.exe" -ArgumentList $args -Wait -PassThru
    if ($p.ExitCode -ne 0 -and $p.ExitCode -ne 3010) {
        Warn2 ("msiexec 返回 {0}，详见日志：{1}" -f $p.ExitCode, $msiLog)
    } else {
        Ok "安装程序执行完毕"
    }

    # 定位实际安装目录（MSI 可能忽略自定义目录）
    $cands = @($Target,
               (Join-Path $env:ProgramFiles "Autopsy-4.23.1"),
               "C:\Program Files\Autopsy-4.23.1",
               (Join-Path $env:ProgramFiles "Autopsy"))
    foreach ($c in $cands) {
        if ($c -and (Test-Path (Join-Path $c "bin\autopsy64.exe"))) { $installedRoot = (Resolve-Path $c).Path; break }
    }
    if (-not $installedRoot) {
        # 兜底：浅层搜索
        foreach ($drv in @("C:","D:","E:")) {
            if (-not (Test-Path $drv)) { continue }
            $hit = Get-ChildItem -Path $drv -Filter "autopsy64.exe" -Recurse -Depth 4 -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($hit) { $installedRoot = Split-Path -Parent (Split-Path -Parent $hit.FullName); break }
        }
    }
    if (-not $installedRoot) { Fail "安装后仍未找到 autopsy64.exe，请查看 MSI 日志"; Stop-Here 1 }
    Ok ("Autopsy 安装于：{0}" -f $installedRoot)
} else {
    if (-not $Target) { $Target = Join-Path $env:ProgramFiles "Autopsy-4.23.1" }
    if (-not (Test-Path (Join-Path $Target "bin\autopsy64.exe"))) { Fail ("指定目录没有 Autopsy：{0}" -f $Target); Stop-Here 1 }
    $installedRoot = (Resolve-Path $Target).Path
    Ok ("跳过安装，直接配置：{0}" -f $installedRoot)
}

# ---------- 3. 检查是否已安装 Autopsy 进程 ----------
if (Get-Process -Name "autopsy64" -ErrorAction SilentlyContinue) {
    Fail "检测到 Autopsy 正在运行，请先完全退出后重试"
    Stop-Here 1
}

# ---------- 4. 套用中文语言包 ----------
Step "写入中文语言包"
if (-not (Test-Path (Join-Path $payload "bundles.json"))) { Fail "安装包不完整：缺少 payload/bundles.json"; Stop-Here 1 }

Add-Type -AssemblyName System.IO.Compression.FileSystem
$bundles = Get-Content (Join-Path $payload "bundles.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$layers = @()
$layersFile = Join-Path $payload "layers.json"
if (Test-Path $layersFile) { $layers = Get-Content $layersFile -Raw -Encoding UTF8 | ConvertFrom-Json }

function Add-ZipEntry($jarPath, $entryName, $srcFile) {
    $zip = [System.IO.Compression.ZipFile]::Open($jarPath, "Update")
    try {
        $old = $zip.GetEntry($entryName)
        if ($old) { $old.Delete() }
        $entry = $zip.CreateEntry($entryName, [System.IO.Compression.CompressionLevel]::Optimal)
        $stream = $entry.Open()
        try { $bytes = [System.IO.File]::ReadAllBytes($srcFile); $stream.Write($bytes, 0, $bytes.Length) }
        finally { $stream.Close() }
    } finally { $zip.Dispose() }
}

function Get-ZipEntryHash($jarPath, $entryName) {
    $zip = [System.IO.Compression.ZipFile]::OpenRead($jarPath)
    try {
        $e = $zip.GetEntry($entryName)
        if (-not $e) { return "" }
        $ms = New-Object System.IO.MemoryStream
        $s = $e.Open(); $s.CopyTo($ms); $s.Close()
        $sha = [System.Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($sha.ComputeHash($ms.ToArray())) -replace "-", "").ToLower()
    } finally { $zip.Dispose() }
}

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
$okN = 0; $skipN = 0
foreach ($b in $bundles) {
    $jar = Join-Path $installedRoot ($b.jar -replace "\\", "\")
    $src = Join-Path $payload $b.file
    if (-not (Test-Path $jar) -or -not (Test-Path $src)) { $skipN++; continue }
    $bak = Join-Path $backupDir ($b.jar -replace "\\", "\")
    if (-not (Test-Path (Split-Path -Parent $bak))) { New-Item -ItemType Directory -Path (Split-Path -Parent $bak) -Force | Out-Null }
    if (-not (Test-Path $bak)) { Copy-Item $jar $bak -Force }
    try { Add-ZipEntry $jar $b.entry $src; $okN++ } catch { $skipN++ }
}
Ok ("资源写入：{0} 个成功，{1} 个跳过" -f $okN, $skipN)

$lOk = 0; $lSkip = 0
foreach ($l in $layers) {
    $jar = Join-Path $installedRoot ($l.jar -replace "\\", "\")
    if (-not (Test-Path $jar)) { $lSkip++; continue }
    $cur = Get-ZipEntryHash $jar $l.entry
    if ($cur -ne $l.expect) { $lSkip++; continue }
    $bak = Join-Path $backupDir ($l.jar -replace "\\", "\")
    if (-not (Test-Path (Split-Path -Parent $bak))) { New-Item -ItemType Directory -Path (Split-Path -Parent $bak) -Force | Out-Null }
    if (-not (Test-Path $bak)) { Copy-Item $jar $bak -Force }
    try { Add-ZipEntry $jar $l.entry (Join-Path $payload $l.file); $lOk++ } catch { $lSkip++ }
}
Ok ("菜单补丁：{0} 个成功，{1} 个跳过（版本不符会自动跳过）" -f $lOk, $lSkip)

# ---------- 5. 界面语言 ----------
Step "设置界面语言"
$conf = Join-Path $installedRoot "AppDataFolder\autopsy\etc\autopsy.conf"
if (Test-Path $conf) {
    $text = Get-Content $conf -Raw -Encoding UTF8
    if ($text -match "-J-Duser\.language=zh") { Ok "autopsy.conf 已包含中文参数" }
    else {
        $i = $text.IndexOf('default_options="')
        if ($i -ge 0) {
            $j = $text.IndexOf('"', $i + 17)
            if ($j -gt 0) {
                $new = $text.Substring(0, $j) + " -J-Duser.language=zh -J-Duser.country=CN" + $text.Substring($j)
                Copy-Item $conf (Join-Path $backupDir "autopsy.conf") -Force -ErrorAction SilentlyContinue
                [System.IO.File]::WriteAllText($conf, $new, (New-Object System.Text.UTF8Encoding($false)))
                Ok "已写入中文语言参数"
            }
        } else { Warn2 "未找到 default_options" }
    }
} else { Warn2 "未找到 autopsy.conf" }

# ---------- 6. 清理菜单缓存 ----------
Step "清理菜单缓存（中文菜单生效的关键）"
foreach ($d in @((Join-Path $env:LOCALAPPDATA "autopsy\Cache\dev"), (Join-Path $env:LOCALAPPDATA "autopsy\Cache"))) {
    if (Test-Path $d) {
        Get-ChildItem $d -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Ok "已清理：$d"
    }
}

# ---------- 7. 桌面快捷方式 ----------
$shortcutPath = ""
if (-not $NoShortcut) {
    Step "创建桌面快捷方式"
    $exe = Join-Path $installedRoot "bin\autopsy64.exe"
    $desktop = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktop "Autopsy 中文版.lnk"
    $made = $false
    try {
        $ws = New-Object -ComObject WScript.Shell
        $sc = $ws.CreateShortcut($shortcutPath)
        $sc.TargetPath = $exe
        $sc.WorkingDirectory = (Split-Path -Parent $exe)
        $sc.IconLocation = $exe + ",0"
        $sc.Description = "Autopsy 4.23.1 简体中文版"
        $sc.Save()
        $made = $true
    } catch {
        Warn2 ("快捷方式创建失败（{0}），改用批处理替代" -f $_.Exception.Message)
    }
    if (-not $made) {
        $shortcutPath = Join-Path $desktop "Autopsy 中文版.bat"
        $content = "@echo off`r`nstart `"`" `"{0}`"`r`n" -f $exe
        [System.IO.File]::WriteAllText($shortcutPath, $content, (New-Object System.Text.UTF8Encoding($false)))
    }
    if (Test-Path $shortcutPath) { Ok ("已创建：{0}" -f $shortcutPath) } else { Warn2 "桌面快捷方式未创建" }
}

# ---------- 8. 自检 ----------
Step "安装结果自检"
$checks = @()

$exe = Join-Path $installedRoot "bin\autopsy64.exe"
$checks += ,@("主程序存在", (Test-Path $exe))

$jit = Join-Path $installedRoot "jre\bin\java.exe"
$checks += ,@("内置 JRE 存在", (Test-Path $jit))

$probe = Join-Path $installedRoot "platform\modules\org-netbeans-core-ui.jar"
$zhOk = $false
if (Test-Path $probe) {
    $zip = [System.IO.Compression.ZipFile]::OpenRead($probe)
    try { $zhOk = ($null -ne $zip.GetEntry("org/netbeans/core/ui/resources/Bundle_zh_CN.properties")) } finally { $zip.Dispose() }
}
$checks += ,@("中文资源已注入", $zhOk)

$conf = Join-Path $installedRoot "AppDataFolder\autopsy\etc\autopsy.conf"
$confOk = $false
if (Test-Path $conf) { $confOk = ((Get-Content $conf -Raw -Encoding UTF8) -match "-J-Duser\.language=zh") }
$checks += ,@("界面语言已设为中文", $confOk)

if (-not $NoShortcut) { $checks += ,@("桌面快捷方式", (Test-Path $shortcutPath)) }

$allOk = $true
foreach ($c in $checks) {
    if ($c[1]) { Write-Host ("    [√] " + $c[0]) -ForegroundColor Green }
    else { Write-Host ("    [×] " + $c[0]) -ForegroundColor Red; $allOk = $false }
}

Write-Host ""
if ($allOk) {
    Write-Host "  安装完成，可以开始使用了。" -ForegroundColor Green
    Write-Host "  首次启动会重建缓存，约 60-90 秒。" -ForegroundColor Gray
    Write-Host "  安装目录：$installedRoot" -ForegroundColor Gray
    Write-Host "  备份目录：$backupDir" -ForegroundColor DarkGray
} else {
    Write-Host "  安装未完全成功，请查看上面的 [×] 项。" -ForegroundColor Yellow
    Write-Host "  可重复运行本脚本，或查看日志：$logDir" -ForegroundColor Gray
}

if (-not $Quiet) {
    Write-Host ""
    $ans = Read-Host "现在启动 Autopsy？(Y/n)"
    if ($ans -ne "n" -and $ans -ne "N") {
        Start-Process -FilePath $exe -WorkingDirectory (Split-Path -Parent $exe)
    }
}
