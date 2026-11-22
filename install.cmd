@echo off
chcp 65001 >nul
setlocal
set ROOT=%~1
if "%ROOT%"=="" set ROOT=%AUTOPSY_HOME%
if "%ROOT%"=="" (
  echo 用法: install.cmd "D:/kit-ascii/autopsy"
  echo   或先设置环境变量 AUTOPSY_HOME
  exit /b 1
)
echo [1/2] 安装语言包 -^> %ROOT%
python "%~dp0scripts\install_pack.py" --root "%ROOT%" --set-locale %2 %3 %4
if errorlevel 1 exit /b 1
echo [2/2] 完成。请关闭并重新启动 Autopsy（首次启动会重建缓存，约 60-90 秒）。
endlocal
