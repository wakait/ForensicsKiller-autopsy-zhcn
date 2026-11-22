@echo off
chcp 65001 >nul
title Autopsy Chinese Pack - Install
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
