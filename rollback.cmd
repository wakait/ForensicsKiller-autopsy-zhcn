@echo off
chcp 65001 >nul
setlocal
set ROOT=%~1
if "%ROOT%"=="" set ROOT=%AUTOPSY_HOME%
if "%ROOT%"=="" (
  echo 用法: rollback.cmd "D:/kit-ascii/autopsy"
  exit /b 1
)
echo 回滚语言包 -^> %ROOT%
python "%~dp0scripts\rollback_pack.py" --yes %2 %3
endlocal
