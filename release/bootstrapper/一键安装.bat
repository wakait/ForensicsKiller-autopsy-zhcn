@echo off
chcp 65001 >nul
title Autopsy 4.23.1 简体中文版 - 一键安装
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
