@echo off
setlocal
call "%~dp0..\world_systems\Uninstall.bat" nopause
if /i not "%~1"=="nopause" pause
