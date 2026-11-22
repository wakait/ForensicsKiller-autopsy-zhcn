@echo off
chcp 65001 >nul
title Autopsy 4.23.1 简体中文便携版
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0启动.ps1" %*
