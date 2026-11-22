@echo off
chcp 65001 >nul
python "%~dp0scripts\verify_new.py"
echo.
python "%~dp0scripts\loadtest_all.py"
