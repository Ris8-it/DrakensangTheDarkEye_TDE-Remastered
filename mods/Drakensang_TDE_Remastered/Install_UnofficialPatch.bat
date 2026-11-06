@echo off
:: Optional: Unofficial Patch (vanilla data fixes). Close the game first. Remove with Uninstall_UnofficialPatch.bat.
setlocal
call "%~dp0..\unofficial_patch\Install.bat" nopause
if /i not "%~1"=="nopause" pause
