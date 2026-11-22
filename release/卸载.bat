@echo off
chcp 65001 >nul
title Autopsy Chinese Pack - Uninstall
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1" %*
