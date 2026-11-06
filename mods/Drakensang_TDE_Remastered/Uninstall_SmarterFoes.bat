@echo off
setlocal
call "%~dp0..\smarter_foes\Uninstall.bat" nopause
if /i not "%~1"=="nopause" pause
