@echo off
setlocal
call "%~dp0..\unofficial_patch\Uninstall.bat" nopause
if /i not "%~1"=="nopause" pause
