@echo off
:: Optional: SmarterFoes (engine layers). Close the game first. Remove with Uninstall_SmarterFoes.bat.
setlocal
call "%~dp0..\smarter_foes\Install.bat" nopause
if /i not "%~1"=="nopause" pause
