@echo off
:: Optional: WorldSystems (engine layers). Close the game first. Remove with Uninstall_WorldSystems.bat.
setlocal
call "%~dp0..\world_systems\Install.bat" nopause
if /i not "%~1"=="nopause" pause
