@echo off
chcp 65001 >nul
title Autopsy 中文版 - 还原英文
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1" %*
