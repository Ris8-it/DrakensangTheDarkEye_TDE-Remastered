@echo off
:: Removes only the optional Hard Ending module. Close the game first.
setlocal
call "%~dp0..\hard_ending\Uninstall.bat" nopause
if /i not "%~1"=="nopause" pause
