@echo off
:: Optional: tougher late-game enemies and bosses (Hard Ending). Close the game first. Remove with Uninstall_HardEnding.bat.
setlocal
call "%~dp0..\hard_ending\Install.bat" nopause
if /i not "%~1"=="nopause" pause
